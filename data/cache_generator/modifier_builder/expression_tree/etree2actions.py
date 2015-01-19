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


from eos.const.eos import Location, Operator
from eos.const.eve import Operand
from .action import Action
from .exception import ETree2ActionError, ExpressionFetchError, ActionValidationError
from .shared import operand_data, state_data


class ETree2Actions:
    """
    Class is responsible for converting tree of Expression objects (which
    aren't directly useful to us) into intermediate Action objects.
    """

    def __init__(self, expressions):
        # Modify expression data rows, so that expression rows are accessible
        # via expression IDs, and data in rows is accessible as attributes
        self._expressions = {}
        for exp_row in expressions:
            self._expressions[exp_row['expressionID']] = exp_row

    def convert(self, tree_root_id, effect_category_id):
        """
        Generate Action objects out of passed data.

        Possible exceptions:
        ETree2ActionError -- raised when tree has documented deviations
        Exception -- any other exception type may be raised, as structure and
        contents of tree may differ from expected greatly, so please wrap call
        into try-except block which catches all exceptions if you want to achieve
        at least basic level of stability
        """
        # Set with already generated actions
        self._actions = []
        # Flag which indicates, did we have data which we
        # have skipped or not
        self._skipped_data = False
        # Run parsing process
        tree_root = self._get_exp(tree_root_id)
        self._generic(tree_root)
        # Validate generated actions
        for action in self._actions:
            if self.validate_action(action, effect_category_id) is not True:
                raise ActionValidationError('failed to validate action')
        return self._actions, self._skipped_data

    def _generic(self, expression):
        """Generic entry point, used if we expect passed node to be meaningful"""
        operand_id = expression.get('operandID')
        try:
            operand_meta = operand_data[operand_id]
        except KeyError:
            operand_enabled_flag = None
        else:
            operand_enabled_flag = operand_meta.enabled
        # For nodes which describe apply/undo action,
        # call method which handles them
        if operand_enabled_flag is True:
            self._make_action(expression)
        # Mark current effect as partially parsed if it contains
        # inactive operands
        elif operand_enabled_flag is False:
            self._skipped_data = True
        # If multiple actions are spliced here, handle it
        # appropriately
        elif expression.get('operandID') == Operand.splice:
            self._splice(expression)
        # Process expressions with other operands using the map
        else:
            generic_opnds = {Operand.def_int: self._check_int_stub,
                             Operand.def_bool: self._check_bool_stub}
            try:
                method = generic_opnds[operand_id]
            except KeyError as e:
                raise ETree2ActionError('unknown generic operand {}'.format(operand_id)) from e
            method(expression)

    def _splice(self, expression):
        """Reference two expressions from single one"""
        arg1 = self._get_exp(expression.get('arg1'))
        self._generic(arg1)
        arg2 = self._get_exp(expression.get('arg2'))
        self._generic(arg2)

    def _make_action(self, expression):
        """Make action for expressions describing modifier"""
        action = Action()
        # Write action type, which corresponds to operand of current
        # expression
        action.type = expression.get('operandID')
        # Request operator and target data, it's always in arg1
        arg1 = self._get_exp(expression.get('arg1'))
        self._optr_tgt(arg1, action)
        # Write down source attribute from arg2
        arg2 = self._get_exp(expression.get('arg2'))
        action.source_attribute_id = self._get_attribute(arg2)
        self._actions.append(action)

    def _optr_tgt(self, expression, action):
        """Get operator and handle target definition"""
        # Operation is always in arg1
        arg1 = self._get_exp(expression.get('arg1'))
        action.operator = self._get_operator(arg1)
        # Handling of arg2 depends on its operand
        tgt_route_map = {Operand.gen_attr: self._tgt_attr,
                         Operand.grp_attr: self._tgt_grp_attr,
                         Operand.srq_attr: self._tgt_srq_attr,
                         Operand.itm_attr: self._tgt_itm_attr}
        arg2 = self._get_exp(expression.get('arg2'))
        tgt_route_map[arg2.get('operandID')](arg2, action)

    def _tgt_attr(self, expression, action):
        """Get target attribute and store it"""
        arg1 = self._get_exp(expression.get('arg1'))
        action.target_attribute_id = self._get_attribute(arg1)

    def _tgt_grp_attr(self, expression, action):
        """Get target group and target attribute"""
        arg1 = self._get_exp(expression.get('arg1'))
        action.target_group_id = self._get_group(arg1)
        arg2 = self._get_exp(expression.get('arg2'))
        action.target_attribute_id = self._get_attribute(arg2)

    def _tgt_srq_attr(self, expression, action):
        """Get target skill requirement and target attribute"""
        arg1 = self._get_exp(expression.get('arg1'))
        self._get_type(arg1, action)
        arg2 = self._get_exp(expression.get('arg2'))
        action.target_attribute_id = self._get_attribute(arg2)

    def _tgt_itm_attr(self, expression, action):
        """Handle target item specification and get target attribute"""
        # Item specification format depends on operand of arg1
        itm_getter_map = {Operand.def_loc: self._tgt_loc,
                          Operand.loc_grp: self._tgt_loc_grp,
                          Operand.loc_srq: self._tgt_loc_srq}
        arg1 = self._get_exp(expression.get('arg1'))
        itm_getter_map[arg1.get('operandID')](arg1, action)
        # Target attribute is always specified in arg2
        arg2 = self._get_exp(expression.get('arg2'))
        action.target_attribute_id = self._get_attribute(arg2)

    def _tgt_loc(self, expression, action):
        """Get target location and store it"""
        action.target_location = self._get_location(expression)

    def _tgt_loc_grp(self, expression, action):
        """Get target location filter and group filter"""
        arg1 = self._get_exp(expression.get('arg1'))
        action.target_location = self._get_location(arg1)
        arg2 = self._get_exp(expression.get('arg2'))
        action.target_group_id = self._get_group(arg2)

    def _tgt_loc_srq(self, expression, action):
        """Get target location filter and skill requirement filter"""
        arg1 = self._get_exp(expression.get('arg1'))
        action.target_location = self._get_location(arg1)
        arg2 = self._get_exp(expression.get('arg2'))
        self._get_type(arg2, action)

    def _check_int_stub(self, expression):
        """Check if given expression is stub, returning integer 0 or 1"""
        value = self._get_integer(expression)
        if value not in (0, 1):
            raise ETree2ActionError('integer stub with unexpected value {}'.format(value))

    def _check_bool_stub(self, expression):
        """Check if given expression is stub, returning boolean true"""
        value = self._get_boolean(expression)
        if value is not True:
            raise ETree2ActionError('boolean stub with unexpected value {}'.format(value))

    def _get_operator(self, expression):
        # Format: {operator name: operator ID}
        conversion_map = {'PreAssignment': Operator.pre_assignment,
                          'PreMul': Operator.pre_mul,
                          'PreDiv': Operator.pre_div,
                          'ModAdd': Operator.mod_add,
                          'ModSub': Operator.mod_sub,
                          'PostMul': Operator.post_mul,
                          'PostDiv': Operator.post_div,
                          'PostPercent': Operator.post_percent,
                          'PostAssignment': Operator.post_assignment}
        operator = conversion_map[expression.get('expressionValue')]
        return operator

    def _get_location(self, expression):
        # Format: {location name: location ID}
        conversion_map = {'Self': Location.self_,
                          'Char': Location.character,
                          'Ship': Location.ship,
                          'Target': Location.target,
                          'Other': Location.other,
                          'Area': Location.area}
        location = conversion_map[expression.get('expressionValue')]
        return location

    def _get_attribute(self, expression):
        attribute = int(expression.get('expressionAttributeID'))
        return attribute

    def _get_group(self, expression):
        group = int(expression.get('expressionGroupID'))
        return group

    def _get_type(self, expression, action):
        # Type getter function has special handling
        if expression.get('operandID') == Operand.get_type:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            arg1 = self._get_exp(expression.get('arg1'))
            if self._get_location(arg1) == Location.self_:
                action.target_skill_requirement_self = True
        else:
            action.target_skill_requirement_id = int(expression.get('expressionTypeID'))

    def _get_integer(self, expression):
        integer = int(expression.get('expressionValue'))
        return integer

    def _get_boolean(self, expression):
        # Format: {boolean name: boolean value}
        conversion_map = {'True': True,
                          'False': False}
        boolean = conversion_map[expression.get('expressionValue')]
        return boolean

    def _get_exp(self, expression_id):
        try:
            return self._expressions[expression_id]
        except KeyError:
            raise ExpressionFetchError(expression_id)

    def validate_action(self, action, effect_category_id):
        """
        Validation of action objects. Run few top-level action type-agnostic
        checks and then route to type-specific check methods.
        """
        # Operator, source attribute and target attributes all must
        # have proper values in any case
        if (
            action.operator not in Operator or
            isinstance(action.source_attribute_id, int) is not True or
            isinstance(action.target_attribute_id, int) is not True
        ):
            return False
        # It should be possible to convert gang flag and effect
        # category ID into state and context
        try:
            operand_meta = operand_data[action.type]
        except KeyError:
            gang_flag = None
        else:
            gang_flag = operand_meta.gang
        if (effect_category_id, gang_flag) not in state_data:
            return False
        # Other fields are optional, check them using action type
        validate_map = {Operand.add_gang_grp_mod: self._validate_gang_grp,
                        Operand.rm_gang_grp_mod: self._validate_gang_grp,
                        Operand.add_gang_itm_mod: self._validate_gang_itm,
                        Operand.rm_gang_itm_mod: self._validate_gang_itm,
                        Operand.add_gang_own_srq_mod: self._validate_gang_own_srq,
                        Operand.rm_gang_own_srq_mod: self._validate_gang_own_srq,
                        Operand.add_gang_srq_mod: self._validate_gang_srq,
                        Operand.rm_gang_srq_mod: self._validate_gang_srq,
                        Operand.add_itm_mod: self._validate_itm,
                        Operand.rm_itm_mod: self._validate_itm,
                        Operand.add_loc_grp_mod: self._validate_loc_grp,
                        Operand.rm_loc_grp_mod: self._validate_loc_grp,
                        Operand.add_loc_mod: self._validate_loc,
                        Operand.rm_loc_mod: self._validate_loc,
                        Operand.add_loc_srq_mod: self._validate_loc_srq,
                        Operand.rm_loc_srq_mod: self._validate_loc_srq,
                        Operand.add_own_srq_mod: self._validate_own_srq,
                        Operand.rm_own_srq_mod: self._validate_own_srq}
        try:
            method = validate_map[action.type]
        except KeyError:
            return False
        return method(action)

    # Block with validating methods, called depending on action type
    def _validate_gang_grp(self, action):
        if (
            action.target_location is not None or
            action.target_skill_requirement_id is not None or
            action.target_skill_requirement_self is not False
        ):
            return False
        if isinstance(action.target_group_id, int) is not True:
            return False
        return True

    def _validate_gang_itm(self, action):
        if (
            action.target_location is not None or
            action.target_group_id is not None or
            action.target_skill_requirement_id is not None or
            action.target_skill_requirement_self is not False
        ):
            return False
        return True

    def _validate_gang_own_srq(self, action):
        if (
            action.target_location is not None or
            action.target_group_id is not None
        ):
            return False
        if self._validate_skill_req(action) is not True:
            return False
        return True

    def _validate_gang_srq(self, action):
        if (
            action.target_location is not None or
            action.target_group_id is not None
        ):
            return False
        if self._validate_skill_req(action) is not True:
            return False
        return True

    def _validate_itm(self, action):
        if (
            action.target_group_id is not None or
            action.target_skill_requirement_id is not None or
            action.target_skill_requirement_self is not False
        ):
            return False
        if action.target_location not in Location:
            return False
        return True

    def _validate_loc_grp(self, action):
        if (
            action.target_skill_requirement_id is not None or
            action.target_skill_requirement_self is not False
        ):
            return False
        valid_locs = (Location.character, Location.ship, Location.target, Location.self_)
        if (
            action.target_location not in valid_locs or
            isinstance(action.target_group_id, int) is not True
        ):
            return False
        return True

    def _validate_loc(self, action):
        if (
            action.target_group_id is not None or
            action.target_skill_requirement_id is not None or
            action.target_skill_requirement_self is not False
        ):
            return False
        valid_locs = (Location.character, Location.ship, Location.target, Location.self_)
        if action.target_location not in valid_locs:
            return False
        return True

    def _validate_loc_srq(self, action):
        if action.target_group_id is not None:
            return False
        valid_locs = (Location.character, Location.ship, Location.target, Location.self_)
        if (
            action.target_location not in valid_locs or
            self._validate_skill_req(action) is not True
        ):
            return False
        return True

    def _validate_own_srq(self, action):
        if action.target_group_id is not None:
            return False
        valid_locs = (Location.character, Location.ship)
        if (
            action.target_location not in valid_locs or
            self._validate_skill_req(action) is not True
        ):
            return False
        return True

    def _validate_skill_req(self, action):
        # We allow to specify skill either via integer ID or via carrier self-reference flag
        if (
            (isinstance(action.target_skill_requirement_id, int) is True and
             action.target_skill_requirement_self is False) or
            (action.target_skill_requirement_id is None and
             action.target_skill_requirement_self is True)
        ):
            return True
        return False
