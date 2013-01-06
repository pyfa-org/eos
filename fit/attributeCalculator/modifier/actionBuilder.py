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


from eos.const import Location, Operator, InvType
from eos.eve.const import Operand
from .action import Action
from .exception import ActionBuilderError, ActionValidationError
from .shared import operandData, stateData


class ActionBuilder:
    """
    Class is responsible for converting tree of Expression objects (which
    aren't directly useful to us) into intermediate Action objects.
    """

    @classmethod
    def build(cls, treeRoot, effectCategoryId):
        """
        Generate Action objects out of passed data.

        Positional arguments:
        treeRoot -- root expression of expression tree
        effectCategoryId -- category of effect whose expressions
        are passed as treeRoot

        Return value:
        Tuple (set with Action objects, skipped data flag), where
        skipped data flag indicates that we have encountered inactive
        operands

        Possible exceptions:
        ActionBuilderError -- raised when tree has documented deviations
        Exception -- any other exception type may be raised, as structure and
        contents of tree may differ from expected greatly, so please wrap call
        into try-except block which catches all exceptions if you want to achieve
        at least basic level of stability
        """
        # Set with already generated actions
        actionsContainer = set()
        # Flag which indicates, did we have data which we
        # have skipped or not
        skippedData = False
        # Run parsing process
        skippedData = cls.__generic(treeRoot, actionsContainer, skippedData)
        # Validate generated actions
        for action in actionsContainer:
            if cls.validateAction(action, effectCategoryId) is not True:
                raise ActionValidationError("failed to validate action")
        return actionsContainer, skippedData

    @classmethod
    def __generic(cls, element, actionsContainer, skippedData):
        """Generic entry point, used if we expect passed node to be meaningful"""
        try:
            operandMeta = operandData[element.operandId]
        except KeyError:
            operandEnabledFlag = None
        else:
            operandEnabledFlag = operandMeta.enabled
        # For nodes which describe apply/undo action,
        # call method which handles them
        if operandEnabledFlag is True:
            cls.__makeAction(element, actionsContainer)
        # Mark current effect as partially parsed if it contains
        # inactive operands
        elif operandEnabledFlag is False:
            skippedData = True
        # If multiple actions are spliced here, handle it
        # appropriately
        elif element.operandId == Operand.splice:
            skippedData = cls.__splice(element, actionsContainer, skippedData)
        # Process expressions with other operands using the map
        else:
            genericOpnds = {Operand.defInt: cls.__checkIntStub,
                            Operand.defBool: cls.__checkBoolStub}
            try:
                method = genericOpnds[element.operandId]
            except KeyError as e:
                raise ActionBuilderError("unknown generic operand {}".format(element.operandId)) from e
            method(element)
        return skippedData

    @classmethod
    def __splice(cls, element, actionsContainer, skippedData):
        """Reference two expressions from single one"""
        skippedData = cls.__generic(element.arg1, actionsContainer, skippedData)
        skippedData = cls.__generic(element.arg2, actionsContainer, skippedData)
        return skippedData

    @classmethod
    def __makeAction(cls, element, actionsContainer):
        """Make action for expressions describing modifier"""
        action = Action()
        # Write action type, which corresponds to operand of current
        # expression
        action.type = element.operandId
        # Request operator and target data, it's always in arg1
        cls.__optrTgt(element.arg1, action)
        # Write down source attribute from arg2
        action.sourceAttributeId = cls.__getAttribute(element.arg2)
        actionsContainer.add(action)

    @classmethod
    def __optrTgt(cls, element, action):
        """Get operator and handle target definition"""
        # Operation is always in arg1
        action.operator = cls.__getOperator(element.arg1)
        # Handling of arg2 depends on its operand
        tgtRouteMap = {Operand.genAttr: cls.__tgtAttr,
                       Operand.grpAttr: cls.__tgtGrpAttr,
                       Operand.srqAttr: cls.__tgtSrqAttr,
                       Operand.itmAttr: cls.__tgtItmAttr}
        tgtRouteMap[element.arg2.operandId](element.arg2, action)

    @classmethod
    def __tgtAttr(cls, element, action):
        """Get target attribute and store it"""
        action.targetAttributeId = cls.__getAttribute(element.arg1)

    @classmethod
    def __tgtGrpAttr(cls, element, action):
        """Get target group and target attribute"""
        action.targetGroupId = cls.__getGroup(element.arg1)
        action.targetAttributeId = cls.__getAttribute(element.arg2)

    @classmethod
    def __tgtSrqAttr(cls, element, action):
        """Get target skill requirement and target attribute"""
        action.targetSkillRequirementId = cls.__getType(element.arg1)
        action.targetAttributeId = cls.__getAttribute(element.arg2)

    @classmethod
    def __tgtItmAttr(cls, element, action):
        """Handle target item specification and get target attribute"""
        # Item specification format depends on operand of arg1
        itmGetterMap = {Operand.defLoc: cls.__tgtLoc,
                        Operand.locGrp: cls.__tgtLocGrp,
                        Operand.locSrq: cls.__tgtLocSrq}
        itmGetterMap[element.arg1.operandId](element.arg1, action)
        # Target attribute is always specified in arg2
        action.targetAttributeId = cls.__getAttribute(element.arg2)

    @classmethod
    def __tgtLoc(cls, element, action):
        """Get target location and store it"""
        action.targetLocation = cls.__getLocation(element)

    @classmethod
    def __tgtLocGrp(cls, element, action):
        """Get target location filter and group filter"""
        action.targetLocation = cls.__getLocation(element.arg1)
        action.targetGroupId = cls.__getGroup(element.arg2)

    @classmethod
    def __tgtLocSrq(cls, element, action):
        """Get target location filter and skill requirement filter"""
        action.targetLocation = cls.__getLocation(element.arg1)
        action.targetSkillRequirementId = cls.__getType(element.arg2)

    @classmethod
    def __checkIntStub(cls, element):
        """Check if given expression is stub, returning integer 0 or 1"""
        value = cls.__getInteger(element)
        if not value in (0, 1):
            raise ActionBuilderError("integer stub with unexpected value {}".format(value))

    @classmethod
    def __checkBoolStub(cls, element):
        """Check if given expression is stub, returning boolean true"""
        value = cls.__getBoolean(element)
        if value is not True:
            raise ActionBuilderError("boolean stub with unexpected value {}".format(value))

    @classmethod
    def __getOperator(cls, expression):
        # Format: {operator name: operator ID}
        conversionMap = {"PreAssignment": Operator.preAssignment,
                         "PreMul": Operator.preMul,
                         "PreDiv": Operator.preDiv,
                         "ModAdd": Operator.modAdd,
                         "ModSub": Operator.modSub,
                         "PostMul": Operator.postMul,
                         "PostDiv": Operator.postDiv,
                         "PostPercent": Operator.postPercent,
                         "PostAssignment": Operator.postAssignment}
        operator = conversionMap[expression.value]
        return operator

    @classmethod
    def __getLocation(cls, expression):
        # Format: {location name: location ID}
        conversionMap = {"Self": Location.self_,
                         "Char": Location.character,
                         "Ship": Location.ship,
                         "Target": Location.target,
                         "Other": Location.other,
                         "Area": Location.area}
        location = conversionMap[expression.value]
        return location

    @classmethod
    def __getAttribute(cls, expression):
        attribute = int(expression.expressionAttributeId)
        return attribute

    @classmethod
    def __getGroup(cls, expression):
        group = int(expression.expressionGroupId)
        return group

    @classmethod
    def __getType(cls, expression):
        # Type getter function has special handling
        if expression.operandId == Operand.getType:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            if cls.__getLocation(expression.arg1) == Location.self_:
                return InvType.self_
            else:
                return None
        else:
            type_ = int(expression.expressionTypeId)
            return type_

    @classmethod
    def __getInteger(cls, expression):
        integer = int(expression.value)
        return integer

    @classmethod
    def __getBoolean(cls, expression):
        # Format: {boolean name: boolean value}
        conversionMap = {"True": True,
                         "False": False}
        boolean = conversionMap[expression.value]
        return boolean

    @classmethod
    def validateAction(cls, action, effectCategoryId):
        """
        Validation of action objects. Run few top-level action type-agnostic
        checks and then route to type-specific check methods.

        Positional arguments:
        action -- action for validation
        effectCategoryId -- category of effect, whose expressions were used
        to generate actions

        Return value:
        False if top-level checks fail, false if no type-specific check
        method isn't found, else transmit value returned by check method
        """
        # Operator, source attribute and target attributes all must
        # have proper values in any case
        if (not action.operator in Operator or
            isinstance(action.sourceAttributeId, int) is not True or
            isinstance(action.targetAttributeId, int) is not True):
            return False
        # It should be possible to convert gang flag and effect
        # category ID into state and context
        try:
            operandMeta = operandData[action.type]
        except KeyError:
            gangFlag = None
        else:
            gangFlag = operandMeta.gang
        if not (effectCategoryId, gangFlag) in stateData:
            return False
        # Other fields are optional, check them using action type
        validateMap = {Operand.addGangGrpMod: cls.__validateGangGrp,
                       Operand.rmGangGrpMod: cls.__validateGangGrp,
                       Operand.addGangItmMod: cls.__validateGangItm,
                       Operand.rmGangItmMod: cls.__validateGangItm,
                       Operand.addGangOwnSrqMod: cls.__validateGangOwnSrq,
                       Operand.rmGangOwnSrqMod: cls.__validateGangOwnSrq,
                       Operand.addGangSrqMod: cls.__validateGangSrq,
                       Operand.rmGangSrqMod: cls.__validateGangSrq,
                       Operand.addItmMod: cls.__validateItm,
                       Operand.rmItmMod: cls.__validateItm,
                       Operand.addLocGrpMod: cls.__validateLocGrp,
                       Operand.rmLocGrpMod: cls.__validateLocGrp,
                       Operand.addLocMod: cls.__validateLoc,
                       Operand.rmLocMod: cls.__validateLoc,
                       Operand.addLocSrqMod: cls.__validateLocSrq,
                       Operand.rmLocSrqMod: cls.__validateLocSrq,
                       Operand.addOwnSrqMod: cls.__validateOwnSrq,
                       Operand.rmOwnSrqMod: cls.__validateOwnSrq}
        try:
            method = validateMap[action.type]
        except KeyError:
            return False
        return method(action)

    # Block with validating methods, called depending on action type
    @classmethod
    def __validateGangGrp(cls, action):
        if action.targetLocation is not None or action.targetSkillRequirementId is not None:
            return False
        if isinstance(action.targetGroupId, int) is not True:
            return False
        return True

    @classmethod
    def __validateGangItm(cls, action):
        if (action.targetLocation is not None or action.targetGroupId is not None or
            action.targetSkillRequirementId is not None):
            return False
        return True

    @classmethod
    def __validateGangOwnSrq(cls, action):
        if action.targetLocation is not None or action.targetGroupId is not None:
            return False
        if isinstance(action.targetSkillRequirementId, int) is not True:
            return False
        return True

    @classmethod
    def __validateGangSrq(cls, action):
        if action.targetLocation is not None or action.targetGroupId is not None:
            return False
        if isinstance(action.targetSkillRequirementId, int) is not True:
            return False
        return True

    @classmethod
    def __validateItm(cls, action):
        if action.targetGroupId is not None or action.targetSkillRequirementId is not None:
            return False
        if not action.targetLocation in Location:
            return False
        return True

    @classmethod
    def __validateLocGrp(cls, action):
        if action.targetSkillRequirementId is not None:
            return False
        validLocs = (Location.character, Location.ship, Location.target, Location.self_)
        if (not action.targetLocation in validLocs or
            isinstance(action.targetGroupId, int) is not True):
            return False
        return True

    @classmethod
    def __validateLoc(cls, action):
        if action.targetGroupId is not None or action.targetSkillRequirementId is not None:
            return False
        validLocs = (Location.character, Location.ship, Location.target, Location.self_)
        if not action.targetLocation in validLocs:
            return False
        return True

    @classmethod
    def __validateLocSrq(cls, action):
        if action.targetGroupId is not None:
            return False
        validLocs = (Location.character, Location.ship, Location.target, Location.self_)
        if (not action.targetLocation in validLocs or
            isinstance(action.targetSkillRequirementId, int) is not True):
            return False
        return True

    @classmethod
    def __validateOwnSrq(cls, action):
        if action.targetGroupId is not None:
            return False
        validLocs = (Location.character, Location.ship)
        if (not action.targetLocation in validLocs or
            isinstance(action.targetSkillRequirementId, int) is not True):
            return False
        return True
