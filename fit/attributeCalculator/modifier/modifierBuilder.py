#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.const import Location, EffectBuildStatus, FilterType
from eos.dataHandler.exception import ExpressionFetchError
from eos.eve.const import Operand
from .actionBuilder import ActionBuilder
from .exception import TreeFetchingError, TreeParsingError, TreeParsingUnexpectedError, UnusedActionError, ActionBuilderError
from .helpers import operandData, stateData
from .modifier import Modifier


class ModifierBuilder:
    """
    Class is responsible for converting Action objects into Modifier
    objects, which can then be used in the rest of the engine.
    """

    @classmethod
    def build(cls, effect, logger):
        """
        Generate Modifier objects out of passed data.

        Positional arguments:
        effect -- effect, for which we're building modifiers
        logger -- instance of logger to use for error reporting

        Return value:
        Tuple (tuple with Modifier objects, build status), where build status
        is eos.const.EffectBuildStatus class' attribute value
        """
        try:
            # By default, assume that our build is 100% successful
            buildStatus = EffectBuildStatus.okFull
            # Containers for our data
            preActions = set()
            postActions = set()

            # Get actions out of both trees
            for treeName, actionSet in (("preExpression", preActions),
                                        ("postExpression", postActions)):
                try:
                    treeRoot = getattr(effect, treeName)
                except ExpressionFetchError as e:
                    raise TreeFetchingError(*e.args)
                # As we already store expressions in local variable,
                # remove reference to them from effect object by
                # deleting corresponding attribute - to not consume
                # memory when building process is finished
                delattr(effect, treeName)
                # If there's no tree, then there's
                # nothing to build
                if treeRoot is None:
                    continue
                try:
                    actions, skippedData = ActionBuilder.build(treeRoot, effect.categoryId)
                # If any errors occurred, raise corresponding exceptions
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
            modifiers = set()
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
                        modifier = cls.actionToModifier(preAction, effect.categoryId)
                        modifiers.add(modifier)
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
            except UnusedActionError:
                msg = "unused actions left after generating modifiers for effect {}".format(effect.id)
                signature = (UnusedActionError, effect.id)
                logger.warning(msg, childName="modifierBuilder", signature=signature)
                buildStatus = EffectBuildStatus.okPartial

        # Handle raised exceptions
        except TreeFetchingError as e:
            msg = "failed to parse expressions of effect {}: unable to fetch expression {}".format(effect.id, e.args[0])
            signature = (TreeFetchingError, effect.id)
            logger.error(msg, childName="modifierBuilder", signature=signature)
            return (), EffectBuildStatus.error
        except TreeParsingError as e:
            msg = "failed to parse expressions of effect {}: {}".format(effect.id, e.args[0])
            signature = (TreeParsingError, effect.id)
            logger.warning(msg, childName="modifierBuilder", signature=signature)
            return (), EffectBuildStatus.error
        except TreeParsingUnexpectedError:
            msg = "failed to parse expressions of effect {} due to unknown reason".format(effect.id)
            signature = (TreeParsingUnexpectedError, effect.id)
            logger.error(msg, childName="modifierBuilder", signature=signature)
            return (), EffectBuildStatus.error

        return tuple(modifiers), buildStatus

    @classmethod
    def actionToModifier(cls, action, effectCategoryId):
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
        conversionMap = {Operand.addGangGrpMod: cls.__convertGangGrp,
                         Operand.rmGangGrpMod: cls.__convertGangGrp,
                         Operand.addGangItmMod: cls.__convertGangItm,
                         Operand.rmGangItmMod: cls.__convertGangItm,
                         Operand.addGangOwnSrqMod: cls.__convertGangOwnSrq,
                         Operand.rmGangOwnSrqMod: cls.__convertGangOwnSrq,
                         Operand.addGangSrqMod: cls.__convertGangSrq,
                         Operand.rmGangSrqMod: cls.__convertGangSrq,
                         Operand.addItmMod: cls.__convertItm,
                         Operand.rmItmMod: cls.__convertItm,
                         Operand.addLocGrpMod: cls.__convertLocGrp,
                         Operand.rmLocGrpMod: cls.__convertLocGrp,
                         Operand.addLocMod: cls.__convertLoc,
                         Operand.rmLocMod: cls.__convertLoc,
                         Operand.addLocSrqMod: cls.__convertLocSrq,
                         Operand.rmLocSrqMod: cls.__convertLocSrq,
                         Operand.addOwnSrqMod: cls.__convertOwnSrq,
                         Operand.rmOwnSrqMod: cls.__convertOwnSrq}
        conversionMap[action.type](action, modifier)
        return modifier

    # Block with conversion methods, called depending on action type
    @classmethod
    def __convertGangGrp(cls, action, modifier):
        modifier.location = Location.ship
        modifier.filterType = FilterType.group
        modifier.filterValue = action.targetGroupId

    @classmethod
    def __convertGangItm(cls, action, modifier):
        modifier.location = Location.ship

    @classmethod
    def __convertGangOwnSrq(cls, action, modifier):
        modifier.location = Location.space
        modifier.filterType = FilterType.skill
        modifier.filterValue = action.targetSkillRequirementId

    @classmethod
    def __convertGangSrq(cls, action, modifier):
        modifier.location = Location.ship
        modifier.filterType = FilterType.skill
        modifier.filterValue = action.targetSkillRequirementId

    @classmethod
    def __convertItm(cls, action, modifier):
        modifier.location = action.targetLocation

    @classmethod
    def __convertLocGrp(cls, action, modifier):
        modifier.location = action.targetLocation
        modifier.filterType = FilterType.group
        modifier.filterValue = action.targetGroupId

    @classmethod
    def __convertLoc(cls, action, modifier):
        modifier.location = action.targetLocation
        modifier.filterType = FilterType.all_

    @classmethod
    def __convertLocSrq(cls, action, modifier):
        modifier.location = action.targetLocation
        modifier.filterType = FilterType.skill
        modifier.filterValue = action.targetSkillRequirementId

    @classmethod
    def __convertOwnSrq(cls, action, modifier):
        modifier.location = Location.space
        modifier.filterType = FilterType.skill
        modifier.filterValue = action.targetSkillRequirementId
