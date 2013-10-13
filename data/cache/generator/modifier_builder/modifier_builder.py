#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from eos.const.eos import Location, EffectBuildStatus, FilterType
from eos.const.eve import Operand
from eos.data.cache.object import Modifier
from .action_builder import ActionBuilder
from .exception import TreeFetchingError, TreeParsingError, TreeParsingUnexpectedError, UnusedActionError, \
    ActionBuilderError, ExpressionFetchError
from .shared import operand_data, state_data


class ModifierBuilder:
    """
    Class is responsible for converting Action objects into Modifier
    objects, which can then be used in the rest of the engine.
    """

    def __init__(self, expressions, logger):
        self._action_builder = ActionBuilder(expressions)
        self._logger = logger

    def build_effect(self, pre_expression_id, post_expression_id, effect_category_id):
        """Generate Modifier objects out of passed data."""
        try:
            # By default, assume that our build is 100% successful
            build_status = EffectBuildStatus.ok_full
            # Containers for our data
            pre_actions = set()
            post_actions = set()

            # Get actions out of both trees
            for tree_root_id, action_set in ((pre_expression_id, pre_actions),
                                             (post_expression_id, post_actions)):
                # If there's no tree, then there's nothing to build
                if tree_root_id is None:
                    continue
                try:
                    actions, skipped_data = self._action_builder.build(tree_root_id, effect_category_id)
                except KeyboardInterrupt:
                    raise
                # If any errors occurred, raise corresponding exceptions
                except ExpressionFetchError as e:
                    raise TreeFetchingError(*e.args)
                except ActionBuilderError as e:
                    raise TreeParsingError(*e.args) from e
                except Exception as e:
                    raise TreeParsingUnexpectedError from e
                # Update set with actions we've just got
                action_set.update(actions)
                # If any skipped data was encountered (for example,
                # inactive operands), change build status
                if skipped_data is True:
                    build_status = EffectBuildStatus.ok_partial

            # Container for actual modifier objects
            modifiers = []
            # Helper containers for action->modifier conversion process
            # Contains references to already used for generation
            # of modifiers pre-actions and post-actions
            used_pre_actions = set()
            used_post_actions = set()

            # To get modifiers, we need two mirror actions, action which
            # applies and action which undoes effect; cycle through
            # pre-actions, which are applying ones
            for pre_action in pre_actions:
                # Cycle through post-actions
                for post_action in post_actions:
                    # Skip actions which we already used
                    if post_action in used_post_actions:
                        continue
                    # If matching pre- and post-actions were detected
                    if pre_action.is_mirror(post_action) is True:
                        # Create actual modifier
                        modifier = self._action_to_modifier(pre_action, effect_category_id)
                        modifiers.append(modifier)
                        # Mark used actions as used
                        used_pre_actions.add(pre_action)
                        used_post_actions.add(post_action)
                        # We found  what we've been looking for in this
                        # post_action loop, thus bail
                        break

            # If there're any actions which were not used for modifier
            # generation, mark current effect as partially parsed
            try:
                if pre_actions.difference(used_pre_actions) or post_actions.difference(used_post_actions):
                    raise UnusedActionError
            except UnusedActionError as e:
                msg = 'unused actions left after parsing tree with base {}-{} and effect category {}'.format(
                    pre_expression_id, post_expression_id, effect_category_id)
                signature = (type(e), pre_expression_id, post_expression_id, effect_category_id)
                self._logger.warning(msg, child_name='modifier_builder', signature=signature)
                build_status = EffectBuildStatus.ok_partial

        # Handle raised exceptions
        except TreeFetchingError as e:
            msg = 'failed to parse tree with base {}-{} and effect category {}: unable to fetch expression {}'.format(
                pre_expression_id, post_expression_id, effect_category_id, e.args[0])
            signature = (type(e), pre_expression_id, post_expression_id, effect_category_id)
            self._logger.error(msg, child_name='modifier_builder', signature=signature)
            return (), EffectBuildStatus.error
        except TreeParsingError as e:
            msg = 'failed to parse tree with base {}-{} and effect category {}: {}'.format(
                pre_expression_id, post_expression_id, effect_category_id, e.args[0])
            signature = (type(e), pre_expression_id, post_expression_id, effect_category_id)
            self._logger.warning(msg, child_name='modifier_builder', signature=signature)
            return (), EffectBuildStatus.error
        except TreeParsingUnexpectedError as e:
            msg = 'failed to parse tree with base {}-{} and effect category {} due to unknown reason'.format(
                pre_expression_id, post_expression_id, effect_category_id)
            signature = (type(e), pre_expression_id, post_expression_id, effect_category_id)
            self._logger.error(msg, child_name='modifier_builder', signature=signature)
            return (), EffectBuildStatus.error

        return modifiers, build_status

    def _action_to_modifier(self, action, effect_category_id):
        """
        Convert action to Modifier object.

        Positional arguments:
        action -- action for conversion
        effect_category_id -- category of effect, whose expressions were used
        to generate action

        Return value:
        Modifier object, generated out of action
        """
        # Create object and fill generic fields
        modifier = Modifier()
        modifier.state, modifier.context = state_data[(effect_category_id, operand_data[action.type].gang)]
        modifier.source_attribute_id = action.source_attribute_id
        modifier.operator = action.operator
        modifier.target_attribute_id = action.target_attribute_id
        # Fill remaining fields on per-type-of-action basis
        conversion_map = {Operand.add_gang_grp_mod: self._convert_gang_grp,
                          Operand.rm_gang_grp_mod: self._convert_gang_grp,
                          Operand.add_gang_itm_mod: self._convert_gang_itm,
                          Operand.rm_gang_itm_mod: self._convert_gang_itm,
                          Operand.add_gang_own_srq_mod: self._convert_gang_own_srq,
                          Operand.rm_gang_own_srq_mod: self._convert_gang_own_srq,
                          Operand.add_gang_srq_mod: self._convert_gang_srq,
                          Operand.rm_gang_srq_mod: self._convert_gang_srq,
                          Operand.add_itm_mod: self._convert_itm,
                          Operand.rm_itm_mod: self._convert_itm,
                          Operand.add_loc_grp_mod: self._convert_loc_grp,
                          Operand.rm_loc_grp_mod: self._convert_loc_grp,
                          Operand.add_loc_mod: self._convert_loc,
                          Operand.rm_loc_mod: self._convert_loc,
                          Operand.add_loc_srq_mod: self._convert_loc_srq,
                          Operand.rm_loc_srq_mod: self._convert_loc_srq,
                          Operand.add_own_srq_mod: self._convert_own_srq,
                          Operand.rm_own_srq_mod: self._convert_own_srq}
        conversion_map[action.type](action, modifier)
        return modifier

    # Block with conversion methods, called depending on action type
    def _convert_gang_grp(self, action, modifier):
        modifier.location = Location.ship
        modifier.filter_type = FilterType.group
        modifier.filter_value = action.target_group_id

    def _convert_gang_itm(self, action, modifier):
        modifier.location = Location.ship

    def _convert_gang_own_srq(self, action, modifier):
        modifier.location = Location.space
        self._fill_srq_filter(action, modifier)

    def _convert_gang_srq(self, action, modifier):
        modifier.location = Location.ship
        self._fill_srq_filter(action, modifier)

    def _convert_itm(self, action, modifier):
        modifier.location = action.target_location

    def _convert_loc_grp(self, action, modifier):
        modifier.location = action.target_location
        modifier.filter_type = FilterType.group
        modifier.filter_value = action.target_group_id

    def _convert_loc(self, action, modifier):
        modifier.location = action.target_location
        modifier.filter_type = FilterType.all_

    def _convert_loc_srq(self, action, modifier):
        modifier.location = action.target_location
        self._fill_srq_filter(action, modifier)

    def _convert_own_srq(self, action, modifier):
        modifier.location = Location.space
        self._fill_srq_filter(action, modifier)

    def _fill_srq_filter(self, action, modifier):
        if (
            action.target_skill_requirement_id is None and
            action.target_skill_requirement_self is True
        ):
            modifier.filter_type = FilterType.skill_self
        else:
            modifier.filter_type = FilterType.skill
            modifier.filter_value = action.target_skill_requirement_id
