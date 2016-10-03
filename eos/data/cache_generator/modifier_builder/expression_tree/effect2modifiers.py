# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from logging import getLogger

from eos.const.eos import Domain, EffectBuildStatus, FilterType
from eos.const.eve import Operand
from eos.data.cache_object import Modifier
from .etree2actions import ETree2Actions
from .exception import TreeParsingUnexpectedError, ETree2ActionError, ExpressionFetchError
from .shared import operand_data, state_data


logger = getLogger(__name__)


class Effect2Modifiers:
    """
    Class which uses effects' expression trees to generate
    actual modifier objects used by Eos.
    """

    def __init__(self, expressions):
        self._etree2actions = ETree2Actions(expressions)

    def convert(self, effect_row):
        """Generate Modifier objects out of passed data."""
        try:
            pre_expression_id = effect_row['pre_expression']
            post_expression_id = effect_row['post_expression']
            effect_category_id = effect_row['effect_category']
            # By default, assume that our build is 100% successful
            build_status = EffectBuildStatus.ok_full
            # Containers for our data
            pre_actions = set()
            post_actions = set()

            # Get actions out of both trees
            for tree_root_id, action_set in (
                (pre_expression_id, pre_actions),
                (post_expression_id, post_actions)
            ):
                # If there's no tree, then there's nothing to build
                if tree_root_id is None:
                    continue
                try:
                    actions, skipped_data = self._etree2actions.convert(tree_root_id, effect_category_id)
                # If any errors occurred, raise corresponding exceptions
                except (KeyboardInterrupt, ExpressionFetchError, ETree2ActionError):
                    raise
                # All exceptions classes besides the ones listed above are considered
                # as unexpected, and will be treated more severely
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
            if pre_actions.difference(used_pre_actions) or post_actions.difference(used_post_actions):
                effect_id = effect_row['effect_id']
                msg = 'unused actions left after parsing expression tree of effect {}'.format(effect_id)
                logger.warning(msg)
                return modifiers, EffectBuildStatus.ok_partial

        # Handle raised exceptions
        except ExpressionFetchError as e:
            effect_id = effect_row['effect_id']
            msg = 'failed to parse expression tree of effect {}: {}'.format(effect_id, e.args[0])
            logger.error(msg)
            return (), EffectBuildStatus.error
        except ETree2ActionError as e:
            effect_id = effect_row['effect_id']
            msg = 'failed to parse expression tree of effect {}: {}'.format(effect_id, e.args[0])
            logger.warning(msg)
            return (), EffectBuildStatus.error
        except TreeParsingUnexpectedError:
            effect_id = effect_row['effect_id']
            msg = 'failed to parse expression tree of effect {} due to unknown reason'.format(effect_id)
            logger.error(msg)
            return (), EffectBuildStatus.error

        return modifiers, build_status

    def _action_to_modifier(self, action, effect_category_id):
        """
        Convert action to Modifier object.

        Required arguments:
        action -- action for conversion
        effect_category_id -- category of effect, whose expressions were used
        to generate action

        Return value:
        Modifier object, generated out of action
        """
        # Create object and fill generic fields
        modifier = Modifier()
        modifier.state, modifier.scope = state_data[(effect_category_id, operand_data[action.type].gang)]
        modifier.src_attr = action.src_attr
        modifier.operator = action.operator
        modifier.tgt_attr = action.tgt_attr
        # Fill remaining fields on per-type-of-action basis
        conversion_map = {
            Operand.add_gang_grp_mod: self._convert_gang_grp,
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
            Operand.rm_own_srq_mod: self._convert_own_srq
        }
        conversion_map[action.type](action, modifier)
        return modifier

    # Block with conversion methods, called depending on action type
    def _convert_gang_grp(self, action, modifier):
        modifier.domain = Domain.ship
        modifier.filter_type = FilterType.group
        modifier.filter_value = action.tgt_group

    def _convert_gang_itm(self, action, modifier):
        modifier.domain = Domain.ship

    def _convert_gang_own_srq(self, action, modifier):
        modifier.domain = Domain.space
        self._fill_srq_filter(action, modifier)

    def _convert_gang_srq(self, action, modifier):
        modifier.domain = Domain.ship
        self._fill_srq_filter(action, modifier)

    def _convert_itm(self, action, modifier):
        modifier.domain = action.domain

    def _convert_loc_grp(self, action, modifier):
        modifier.domain = action.domain
        modifier.filter_type = FilterType.group
        modifier.filter_value = action.tgt_group

    def _convert_loc(self, action, modifier):
        modifier.domain = action.domain
        modifier.filter_type = FilterType.all_

    def _convert_loc_srq(self, action, modifier):
        modifier.domain = action.domain
        self._fill_srq_filter(action, modifier)

    def _convert_own_srq(self, action, modifier):
        modifier.domain = Domain.space
        self._fill_srq_filter(action, modifier)

    def _fill_srq_filter(self, action, modifier):
        if (
            action.tgt_skillrq is None and
            action.tgt_skillrq_self is True
        ):
            modifier.filter_type = FilterType.skill_self
        else:
            modifier.filter_type = FilterType.skill
            modifier.filter_value = action.tgt_skillrq
