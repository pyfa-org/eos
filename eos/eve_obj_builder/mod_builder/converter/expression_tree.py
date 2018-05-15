# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from eos.const.eos import EosTypeId
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModAffecteeFilter
from eos.const.eve import OperandId
from eos.eve_obj.modifier import DogmaModifier
from eos.eve_obj_builder.mod_builder.exception import (
    UnknownEtreeRootOperandError)
from eos.util.attrdict import attrdict


class ExpressionTreeConverter:
    """Converts expression tree into modifiers.

    Args:
        exp_rows: Iterable with expression rows which should be used as data
            source.
    """

    def __init__(self, exp_rows):
        self._fail_count = None
        self._mods = None
        self.__exp_rows = self.__prepare_exp_rows(exp_rows)

    def convert(self, pre_exp_root_id):
        """Generate modifiers.

        Args:
            pre_exp_root_id: Pre-expression ID which points to expression tree
                root, which should be used to generate modifiers. Post-
                expression part is not needed because it always mirrors pre-
                expression in cases where source data is not broken.

        Returns:
            Tuple with iterable which contains modifiers, and quantity of
            modifier build failures we recorded.

        Raises:
            UnknownEtreeRootOperandError: If root expression row contains
                operand with ID we do not know how to handle.
        """
        self._fail_count = 0
        self._mods = []
        root_exp_row = self.__exp_rows.get(pre_exp_root_id)
        self._parse(root_exp_row, root=True)
        return self._mods, self._fail_count

    def _parse(self, exp_row, root=False):
        operand_id = exp_row.get('operandID')
        handler_map = {
            OperandId.splice: self._handle_splice,
            OperandId.add_itm_mod: self._handle_item_mod,
            OperandId.add_dom_mod: self._handle_domain_mod,
            OperandId.add_dom_grp_mod: self._handle_domain_group_mod,
            OperandId.add_dom_srq_mod: self._handle_domain_skillrq_mod,
            OperandId.add_own_srq_mod: self._handle_owner_skillrq_mod}
        try:
            handler = handler_map[operand_id]
        except KeyError as e:
            if root:
                msg = 'unknown root operand ID {}'.format(operand_id)
                raise UnknownEtreeRootOperandError(msg) from e
            # If we are not on root (came here via at least one splice), and if
            # we do not know what to do, consider it as build error
            else:
                self._fail_count += 1
                return
        else:
            try:
                handler(exp_row)
            except KeyboardInterrupt:
                raise
            # If there're any kind of errors in handler, also consider it as
            # build failure
            except Exception:
                self._fail_count += 1
                return

    def _handle_splice(self, exp_row):
        self._parse(exp_row.arg1)
        self._parse(exp_row.arg2)

    def _handle_item_mod(self, exp_row):
        self._mods.append(DogmaModifier(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=self._get_domain(exp_row.arg1.arg2.arg1),
            affectee_attr_id=self._get_attr_id(exp_row.arg1.arg2.arg2),
            operator=self._get_operator(exp_row.arg1.arg1),
            affector_attr_id=self._get_attr_id(exp_row.arg2)))

    def _handle_domain_mod(self, exp_row):
        self._mods.append(DogmaModifier(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=self._get_domain(exp_row.arg1.arg2.arg1),
            affectee_attr_id=self._get_attr_id(exp_row.arg1.arg2.arg2),
            operator=self._get_operator(exp_row.arg1.arg1),
            affector_attr_id=self._get_attr_id(exp_row.arg2)))

    def _handle_domain_group_mod(self, exp_row):
        self._mods.append(DogmaModifier(
            affectee_filter=ModAffecteeFilter.domain_group,
            affectee_domain=self._get_domain(exp_row.arg1.arg2.arg1.arg1),
            affectee_filter_extra_arg=self._get_group_id(
                exp_row.arg1.arg2.arg1.arg2),
            affectee_attr_id=self._get_attr_id(exp_row.arg1.arg2.arg2),
            operator=self._get_operator(exp_row.arg1.arg1),
            affector_attr_id=self._get_attr_id(exp_row.arg2)))

    def _handle_domain_skillrq_mod(self, exp_row):
        self._mods.append(DogmaModifier(
            affectee_filter=ModAffecteeFilter.domain_skillrq,
            affectee_domain=self._get_domain(exp_row.arg1.arg2.arg1.arg1),
            affectee_filter_extra_arg=self._get_type_id(
                exp_row.arg1.arg2.arg1.arg2),
            affectee_attr_id=self._get_attr_id(exp_row.arg1.arg2.arg2),
            operator=self._get_operator(exp_row.arg1.arg1),
            affector_attr_id=self._get_attr_id(exp_row.arg2)))

    def _handle_owner_skillrq_mod(self, exp_row):
        self._mods.append(DogmaModifier(
            affectee_filter=ModAffecteeFilter.owner_skillrq,
            affectee_domain=self._get_domain(exp_row.arg1.arg2.arg1.arg1),
            affectee_filter_extra_arg=self._get_type_id(
                exp_row.arg1.arg2.arg1.arg2),
            affectee_attr_id=self._get_attr_id(exp_row.arg1.arg2.arg2),
            operator=self._get_operator(exp_row.arg1.arg1),
            affector_attr_id=self._get_attr_id(exp_row.arg2)))

    @staticmethod
    def _get_domain(exp_row):
        if exp_row['operandID'] != OperandId.def_dom:
            return None
        conversion_map = {
            'Self': ModDomain.self,
            'Char': ModDomain.character,
            'Ship': ModDomain.ship,
            'Target': ModDomain.target,
            'Other': ModDomain.other}
        return conversion_map[exp_row['expressionValue']]

    @staticmethod
    def _get_operator(exp_row):
        if exp_row['operandID'] != OperandId.def_optr:
            return None
        conversion_map = {
            'PreAssignment': ModOperator.pre_assign,
            'PreMul': ModOperator.pre_mul,
            'PreDiv': ModOperator.pre_div,
            'ModAdd': ModOperator.mod_add,
            'ModSub': ModOperator.mod_sub,
            'PostMul': ModOperator.post_mul,
            'PostDiv': ModOperator.post_div,
            'PostPercent': ModOperator.post_percent,
            'PostAssignment': ModOperator.post_assign}
        return conversion_map[exp_row['expressionValue']]

    @staticmethod
    def _get_attr_id(exp_row):
        if exp_row['operandID'] != OperandId.def_attr:
            return None
        return int(exp_row['expressionAttributeID'])

    @staticmethod
    def _get_type_id(exp_row):
        operand_id = exp_row['operandID']
        if operand_id == OperandId.def_type:
            return int(exp_row['expressionTypeID'])
        # Operand get_type specifies domain in its arg1; typeID of this domain
        # should be taken when needed
        elif operand_id == OperandId.get_type:
            conversion_map = {ModDomain.self: EosTypeId.current_self}
            domain = ExpressionTreeConverter._get_domain(exp_row.arg1)
            return conversion_map[domain]
        else:
            return None

    @staticmethod
    def _get_group_id(exp_row):
        if exp_row['operandID'] != OperandId.def_grp:
            return None
        return int(exp_row['expressionGroupID'])

    @staticmethod
    def __prepare_exp_rows(exp_rows):
        # Convert regular dictionaries into custom dictionaries for easier
        # attribute access
        processed = {}
        for exp_row in exp_rows:
            processed[exp_row['expressionID']] = attrdict(exp_row)
        # Replace expression IDs in arg1/arg2 with actual expressions
        for exp_row in processed.values():
            exp_row.arg1 = processed.get(exp_row.arg1)
            exp_row.arg2 = processed.get(exp_row.arg2)
        return processed
