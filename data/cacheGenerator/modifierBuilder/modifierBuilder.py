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
from eos.eve import Modifier
from .actionBuilder import ActionBuilder
from .exception import TreeFetchingError, TreeParsingError, TreeParsingUnexpectedError, UnusedActionError, ActionBuilderError, ExpressionFetchError
from .shared import operandData, stateData


class ModifierBuilder:
    """
    Class is responsible for converting Action objects into Modifier
    objects, which can then be used in the rest of the engine.
    """

    def __init__(self, expressions, logger):
        self._actionBuilder = ActionBuilder(expressions)
        self._logger = logger

    def buildEffect(self, preExpressionId, postExpressionId, effectCategoryId):
        """Generate Modifier objects out of passed data."""
        try:
            # By default, assume that our build is 100% successful
            buildStatus = EffectBuildStatus.okFull
            # Containers for our data
            preActions = set()
            postActions = set()

            # Get actions out of both trees
            for treeRootId, actionSet in ((preExpressionId, preActions),
                                          (postExpressionId, postActions)):
                # If there's no tree, then there's nothing to build
                if treeRootId is None:
                    continue
                try:
                    actions, skippedData = self._actionBuilder.build(treeRootId, effectCategoryId)
                # If any errors occurred, raise corresponding exceptions
                except ExpressionFetchError as e:
                    raise TreeFetchingError(*e.args)
                except ActionBuilderError as e:
                    raise TreeParsingError(*e.args) from e
                except Exception as e:
                    raise TreeParsingUnexpectedError from e
                # Update set with actions we've just got
                actionSet.update(actions)
                # If any skipped data was encountered (for example,
                # inactive operands), change build status
                if skippedData is True:
                    buildStatus = EffectBuildStatus.okPartial

            # Container for actual modifier objects
            modifiers = []
            # Helper containers for action->modifier conversion process
            # Contains references to already used for generation
            # of modifiers pre-actions and post-actions
            usedPreActions = set()
            usedPostActions = set()

            # To get modifiers, we need two mirror actions, action which
            # applies and action which undoes effect; cycle through
            # pre-actions, which are applying ones
            for preAction in preActions:
                # Cycle through post-actions
                for postAction in postActions:
                    # Skip actions which we already used
                    if postAction in usedPostActions:
                        continue
                    # If matching pre- and post-actions were detected
                    if preAction.isMirror(postAction) is True:
                        # Create actual modifier
                        modifier = self._actionToModifier(preAction, effectCategoryId)
                        modifiers.append(modifier)
                        # Mark used actions as used
                        usedPreActions.add(preAction)
                        usedPostActions.add(postAction)
                        # We found  what we've been looking for in this
                        # postAction loop, thus bail
                        break

            # If there're any actions which were not used for modifier
            # generation, mark current effect as partially parsed
            try:
                if preActions.difference(usedPreActions) or postActions.difference(usedPostActions):
                    raise UnusedActionError
            except UnusedActionError as e:
                msg = 'unused actions left after parsing tree with base {}-{} and effect category {}'.format(preExpressionId, postExpressionId, effectCategoryId)
                signature = (type(e), preExpressionId, postExpressionId, effectCategoryId)
                self._logger.warning(msg, childName='modifierBuilder', signature=signature)
                buildStatus = EffectBuildStatus.okPartial

        # Handle raised exceptions
        except TreeFetchingError as e:
            msg = 'failed to parse tree with base {}-{} and effect category {}: unable to fetch expression {}'.format(preExpressionId, postExpressionId, effectCategoryId, e.args[0])
            signature = (type(e), preExpressionId, postExpressionId, effectCategoryId)
            self._logger.error(msg, childName='modifierBuilder', signature=signature)
            return (), EffectBuildStatus.error
        except TreeParsingError as e:
            msg = 'failed to parse tree with base {}-{} and effect category {}: {}'.format(preExpressionId, postExpressionId, effectCategoryId, e.args[0])
            signature = (type(e), preExpressionId, postExpressionId, effectCategoryId)
            self._logger.warning(msg, childName='modifierBuilder', signature=signature)
            return (), EffectBuildStatus.error
        except TreeParsingUnexpectedError as e:
            msg = 'failed to parse tree with base {}-{} and effect category {} due to unknown reason'.format(preExpressionId, postExpressionId, effectCategoryId)
            signature = (type(e), preExpressionId, postExpressionId, effectCategoryId)
            self._logger.error(msg, childName='modifierBuilder', signature=signature)
            return (), EffectBuildStatus.error

        return modifiers, buildStatus

    def _actionToModifier(self, action, effectCategoryId):
        """
        Convert action to Modifier object.

        Positional arguments:
        action -- action for conversion
        effectCategoryId -- category of effect, whose expressions were used
        to generate action

        Return value:
        Modifier object, generated out of action
        """
        # Create object and fill generic fields
        modifier = Modifier()
        modifier.state, modifier.context = stateData[(effectCategoryId, operandData[action.type].gang)]
        modifier.sourceAttributeId = action.sourceAttributeId
        modifier.operator = action.operator
        modifier.targetAttributeId = action.targetAttributeId
        # Fill remaining fields on per-type-of-action basis
        conversionMap = {Operand.addGangGrpMod: self._convertGangGrp,
                         Operand.rmGangGrpMod: self._convertGangGrp,
                         Operand.addGangItmMod: self._convertGangItm,
                         Operand.rmGangItmMod: self._convertGangItm,
                         Operand.addGangOwnSrqMod: self._convertGangOwnSrq,
                         Operand.rmGangOwnSrqMod: self._convertGangOwnSrq,
                         Operand.addGangSrqMod: self._convertGangSrq,
                         Operand.rmGangSrqMod: self._convertGangSrq,
                         Operand.addItmMod: self._convertItm,
                         Operand.rmItmMod: self._convertItm,
                         Operand.addLocGrpMod: self._convertLocGrp,
                         Operand.rmLocGrpMod: self._convertLocGrp,
                         Operand.addLocMod: self._convertLoc,
                         Operand.rmLocMod: self._convertLoc,
                         Operand.addLocSrqMod: self._convertLocSrq,
                         Operand.rmLocSrqMod: self._convertLocSrq,
                         Operand.addOwnSrqMod: self._convertOwnSrq,
                         Operand.rmOwnSrqMod: self._convertOwnSrq}
        conversionMap[action.type](action, modifier)
        return modifier

    # Block with conversion methods, called depending on action type
    def _convertGangGrp(self, action, modifier):
        modifier.location = Location.ship
        modifier.filterType = FilterType.group
        modifier.filterValue = action.targetGroupId

    def _convertGangItm(self, action, modifier):
        modifier.location = Location.ship

    def _convertGangOwnSrq(self, action, modifier):
        modifier.location = Location.space
        self._fillSrqFilter(action, modifier)

    def _convertGangSrq(self, action, modifier):
        modifier.location = Location.ship
        self._fillSrqFilter(action, modifier)

    def _convertItm(self, action, modifier):
        modifier.location = action.targetLocation

    def _convertLocGrp(self, action, modifier):
        modifier.location = action.targetLocation
        modifier.filterType = FilterType.group
        modifier.filterValue = action.targetGroupId

    def _convertLoc(self, action, modifier):
        modifier.location = action.targetLocation
        modifier.filterType = FilterType.all_

    def _convertLocSrq(self, action, modifier):
        modifier.location = action.targetLocation
        self._fillSrqFilter(action, modifier)

    def _convertOwnSrq(self, action, modifier):
        modifier.location = Location.space
        self._fillSrqFilter(action, modifier)

    def _fillSrqFilter(self, action, modifier):
        if action.targetSkillRequirementId is None and action.targetSkillRequirementSelf is True:
            modifier.filterType = FilterType.skillSelf
        else:
            modifier.filterType = FilterType.skill
            modifier.filterValue = action.targetSkillRequirementId
