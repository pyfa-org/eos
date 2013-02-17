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


from eos.const import Location, Operator
from eos.eve.const import Operand
from .action import Action
from .exception import ActionBuilderError, ExpressionFetchError, ActionValidationError
from .shared import operandData, stateData


class ActionBuilder:
    """
    Class is responsible for converting tree of Expression objects (which
    aren't directly useful to us) into intermediate Action objects.
    """

    def __init__(self, expressions):
        # Modify expression data rows, so that expression rows are accessible
        # via expression IDs, and data in rows is accessible as attributes
        self._expressions = {}
        for expRow in expressions:
            self._expressions[expRow['expressionID']] = expRow

    def build(self, treeRootId, effectCategoryId):
        """
        Generate Action objects out of passed data.

        Possible exceptions:
        ActionBuilderError -- raised when tree has documented deviations
        Exception -- any other exception type may be raised, as structure and
        contents of tree may differ from expected greatly, so please wrap call
        into try-except block which catches all exceptions if you want to achieve
        at least basic level of stability
        """
        # Set with already generated actions
        self._actions = []
        # Flag which indicates, did we have data which we
        # have skipped or not
        self._skippedData = False
        # Run parsing process
        treeRoot = self._getExp(treeRootId)
        self._generic(treeRoot)
        # Validate generated actions
        for action in self._actions:
            if self.validateAction(action, effectCategoryId) is not True:
                raise ActionValidationError('failed to validate action')
        return self._actions, self._skippedData

    def _generic(self, expression):
        """Generic entry point, used if we expect passed node to be meaningful"""
        try:
            operandMeta = operandData[expression.get('operandID')]
        except KeyError:
            operandEnabledFlag = None
        else:
            operandEnabledFlag = operandMeta.enabled
        # For nodes which describe apply/undo action,
        # call method which handles them
        if operandEnabledFlag is True:
            self._makeAction(expression)
        # Mark current effect as partially parsed if it contains
        # inactive operands
        elif operandEnabledFlag is False:
            self._skippedData = True
        # If multiple actions are spliced here, handle it
        # appropriately
        elif expression.get('operandID') == Operand.splice:
            self._skippedData = self._splice(expression)
        # Process expressions with other operands using the map
        else:
            genericOpnds = {Operand.defInt: self._checkIntStub,
                            Operand.defBool: self._checkBoolStub}
            try:
                method = genericOpnds[expression.get('operandID')]
            except KeyError as e:
                raise ActionBuilderError('unknown generic operand {}'.format(expression.get('operandID'))) from e
            method(expression)

    def _splice(self, expression):
        """Reference two expressions from single one"""
        arg1 = self._getExp(expression.get('arg1'))
        self._generic(arg1)
        arg2 = self._getExp(expression.get('arg2'))
        self._generic(arg2)

    def _makeAction(self, expression):
        """Make action for expressions describing modifier"""
        action = Action()
        # Write action type, which corresponds to operand of current
        # expression
        action.type = expression.get('operandID')
        # Request operator and target data, it's always in arg1
        arg1 = self._getExp(expression.get('arg1'))
        self._optrTgt(arg1, action)
        # Write down source attribute from arg2
        arg2 = self._getExp(expression.get('arg2'))
        action.sourceAttributeId = self._getAttribute(arg2)
        self._actions.append(action)

    def _optrTgt(self, expression, action):
        """Get operator and handle target definition"""
        # Operation is always in arg1
        arg1 = self._getExp(expression.get('arg1'))
        action.operator = self._getOperator(arg1)
        # Handling of arg2 depends on its operand
        tgtRouteMap = {Operand.genAttr: self._tgtAttr,
                       Operand.grpAttr: self._tgtGrpAttr,
                       Operand.srqAttr: self._tgtSrqAttr,
                       Operand.itmAttr: self._tgtItmAttr}
        arg2 = self._getExp(expression.get('arg2'))
        tgtRouteMap[arg2.get('operandID')](arg2, action)

    def _tgtAttr(self, expression, action):
        """Get target attribute and store it"""
        arg1 = self._getExp(expression.get('arg1'))
        action.targetAttributeId = self._getAttribute(arg1)

    def _tgtGrpAttr(self, expression, action):
        """Get target group and target attribute"""
        arg1 = self._getExp(expression.get('arg1'))
        action.targetGroupId = self._getGroup(arg1)
        arg2 = self._getExp(expression.get('arg2'))
        action.targetAttributeId = self._getAttribute(arg2)

    def _tgtSrqAttr(self, expression, action):
        """Get target skill requirement and target attribute"""
        arg1 = self._getExp(expression.get('arg1'))
        self._getType(arg1, action)
        arg2 = self._getExp(expression.get('arg2'))
        action.targetAttributeId = self._getAttribute(arg2)

    def _tgtItmAttr(self, expression, action):
        """Handle target item specification and get target attribute"""
        # Item specification format depends on operand of arg1
        itmGetterMap = {Operand.defLoc: self._tgtLoc,
                        Operand.locGrp: self._tgtLocGrp,
                        Operand.locSrq: self._tgtLocSrq}
        arg1 = self._getExp(expression.get('arg1'))
        itmGetterMap[arg1.get('operandID')](arg1, action)
        # Target attribute is always specified in arg2
        arg2 = self._getExp(expression.get('arg2'))
        action.targetAttributeId = self._getAttribute(arg2)

    def _tgtLoc(self, expression, action):
        """Get target location and store it"""
        action.targetLocation = self._getLocation(expression)

    def _tgtLocGrp(self, expression, action):
        """Get target location filter and group filter"""
        arg1 = self._getExp(expression.get('arg1'))
        action.targetLocation = self._getLocation(arg1)
        arg2 = self._getExp(expression.get('arg2'))
        action.targetGroupId = self._getGroup(arg2)

    def _tgtLocSrq(self, expression, action):
        """Get target location filter and skill requirement filter"""
        arg1 = self._getExp(expression.get('arg1'))
        action.targetLocation = self._getLocation(arg1)
        arg2 = self._getExp(expression.get('arg2'))
        self._getType(arg2, action)

    def _checkIntStub(self, expression):
        """Check if given expression is stub, returning integer 0 or 1"""
        value = self._getInteger(expression)
        if not value in (0, 1):
            raise ActionBuilderError('integer stub with unexpected value {}'.format(value))

    def _checkBoolStub(self, expression):
        """Check if given expression is stub, returning boolean true"""
        value = self._getBoolean(expression)
        if value is not True:
            raise ActionBuilderError('boolean stub with unexpected value {}'.format(value))

    def _getOperator(self, expression):
        # Format: {operator name: operator ID}
        conversionMap = {'PreAssignment': Operator.preAssignment,
                         'PreMul': Operator.preMul,
                         'PreDiv': Operator.preDiv,
                         'ModAdd': Operator.modAdd,
                         'ModSub': Operator.modSub,
                         'PostMul': Operator.postMul,
                         'PostDiv': Operator.postDiv,
                         'PostPercent': Operator.postPercent,
                         'PostAssignment': Operator.postAssignment}
        operator = conversionMap[expression.get('expressionValue')]
        return operator

    def _getLocation(self, expression):
        # Format: {location name: location ID}
        conversionMap = {'Self': Location.self_,
                         'Char': Location.character,
                         'Ship': Location.ship,
                         'Target': Location.target,
                         'Other': Location.other,
                         'Area': Location.area}
        location = conversionMap[expression.get('expressionValue')]
        return location

    def _getAttribute(self, expression):
        attribute = int(expression.get('expressionAttributeID'))
        return attribute

    def _getGroup(self, expression):
        group = int(expression.get('expressionGroupID'))
        return group

    def _getType(self, expression, action):
        # Type getter function has special handling
        if expression.get('operandID') == Operand.getType:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            arg1 = self._getExp(expression.get('arg1'))
            if self._getLocation(arg1) == Location.self_:
                action.targetSkillRequirementSelf = True
        else:
            action.targetSkillRequirementId = int(expression.get('expressionTypeID'))

    def _getInteger(self, expression):
        integer = int(expression.get('expressionValue'))
        return integer

    def _getBoolean(self, expression):
        # Format: {boolean name: boolean value}
        conversionMap = {'True': True,
                         'False': False}
        boolean = conversionMap[expression.get('expressionValue')]
        return boolean

    def _getExp(self, expressionId):
        try:
            return self._expressions[expressionId]
        except KeyError:
            raise ExpressionFetchError(expressionId)


    def validateAction(self, action, effectCategoryId):
        """
        Validation of action objects. Run few top-level action type-agnostic
        checks and then route to type-specific check methods.
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
        validateMap = {Operand.addGangGrpMod: self._validateGangGrp,
                       Operand.rmGangGrpMod: self._validateGangGrp,
                       Operand.addGangItmMod: self._validateGangItm,
                       Operand.rmGangItmMod: self._validateGangItm,
                       Operand.addGangOwnSrqMod: self._validateGangOwnSrq,
                       Operand.rmGangOwnSrqMod: self._validateGangOwnSrq,
                       Operand.addGangSrqMod: self._validateGangSrq,
                       Operand.rmGangSrqMod: self._validateGangSrq,
                       Operand.addItmMod: self._validateItm,
                       Operand.rmItmMod: self._validateItm,
                       Operand.addLocGrpMod: self._validateLocGrp,
                       Operand.rmLocGrpMod: self._validateLocGrp,
                       Operand.addLocMod: self._validateLoc,
                       Operand.rmLocMod: self._validateLoc,
                       Operand.addLocSrqMod: self._validateLocSrq,
                       Operand.rmLocSrqMod: self._validateLocSrq,
                       Operand.addOwnSrqMod: self._validateOwnSrq,
                       Operand.rmOwnSrqMod: self._validateOwnSrq}
        try:
            method = validateMap[action.type]
        except KeyError:
            return False
        return method(action)

    # Block with validating methods, called depending on action type
    def _validateGangGrp(self, action):
        if (action.targetLocation is not None or action.targetSkillRequirementId is not None or
            action.targetSkillRequirementSelf is not False):
            return False
        if isinstance(action.targetGroupId, int) is not True:
            return False
        return True

    def _validateGangItm(self, action):
        if (action.targetLocation is not None or action.targetGroupId is not None or
            action.targetSkillRequirementId is not None or action.targetSkillRequirementSelf is not False):
            return False
        return True

    def _validateGangOwnSrq(self, action):
        if action.targetLocation is not None or action.targetGroupId is not None:
            return False
        if self._checkSkillReq(action) is not True:
            return False
        return True

    def _validateGangSrq(self, action):
        if action.targetLocation is not None or action.targetGroupId is not None:
            return False
        if self._checkSkillReq(action) is not True:
            return False
        return True

    def _validateItm(self, action):
        if (action.targetGroupId is not None or action.targetSkillRequirementId is not None or
            action.targetSkillRequirementSelf is not False):
            return False
        if action.targetLocation not in Location:
            return False
        return True

    def _validateLocGrp(self, action):
        if action.targetSkillRequirementId is not None or action.targetSkillRequirementSelf is not False:
            return False
        validLocs = (Location.character, Location.ship, Location.target, Location.self_)
        if (action.targetLocation not in validLocs or
            isinstance(action.targetGroupId, int) is not True):
            return False
        return True

    def _validateLoc(self, action):
        if (action.targetGroupId is not None or action.targetSkillRequirementId is not None or
            action.targetSkillRequirementSelf is not False):
            return False
        validLocs = (Location.character, Location.ship, Location.target, Location.self_)
        if action.targetLocation not in validLocs:
            return False
        return True

    def _validateLocSrq(self, action):
        if action.targetGroupId is not None:
            return False
        validLocs = (Location.character, Location.ship, Location.target, Location.self_)
        if action.targetLocation not in validLocs or self._checkSkillReq(action) is not True:
            return False
        return True

    def _validateOwnSrq(self, action):
        if action.targetGroupId is not None:
            return False
        validLocs = (Location.character, Location.ship)
        if action.targetLocation not in validLocs or self._checkSkillReq(action) is not True:
            return False
        return True

    def _checkSkillReq(self, action):
        # We allow to specify skill either via integer ID or via carrier self-reference flag
        if ((isinstance(action.targetSkillRequirementId, int) is True and action.targetSkillRequirementSelf is False) or
            (action.targetSkillRequirementId is None and action.targetSkillRequirementSelf is True)):
            return True
        return False
