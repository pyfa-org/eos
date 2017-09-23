# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator, EosType
from eos.const.eve import Operand
from eos.eve_object import DogmaModifier
from eos.util.attribute_dict import AttributeDict
from ..exception import UnknownEtreeRootOperandError


class ExpressionTreeConverter:
    """
    Class which uses effects' expression trees to generate
    actual modifier objects used by Eos.
    """

    def __init__(self, expressions):
        self._build_failures = None
        self._modifiers = None
        self.__expressions = self.__prepare_expressions(expressions)

    def convert(self, pre_root_id):
        """Generate *Modifier objects for passed effect."""
        # Initialize instance attributes which
        # will be used during conversion
        self._build_failures = 0
        self._modifiers = []
        # Run conversion
        root_expression = self.__expressions.get(pre_root_id)
        self._parse(root_expression, root=True)
        return self._modifiers, self._build_failures

    def _parse(self, expression, root=False):
        operand = expression.get('operandID')
        handler_map = {
            Operand.splice: self._handle_splice,
            Operand.add_itm_mod: self._handle_item_modifier,
            Operand.add_dom_mod: self._handle_domain_modifier,
            Operand.add_dom_grp_mod: self._handle_domain_group_modifier,
            Operand.add_dom_srq_mod: self._handle_domain_skillrq_modifer,
            Operand.add_own_srq_mod: self._handle_owner_skillrq_modifer
        }
        try:
            handler = handler_map[operand]
        except KeyError as e:
            if root is True:
                msg = 'unknown root operand {}'.format(operand)
                raise UnknownEtreeRootOperandError(msg) from e
            # If we are not on root (came here via at least one splice),
            # and if we do not know what to do, consider it as build error
            else:
                self._build_failures += 1
                return
        else:
            try:
                handler(expression)
            except KeyboardInterrupt:
                raise
            # If there're any kind of errors in handler, also consider
            # it as build failure
            except Exception:
                self._build_failures += 1
                return

    def _handle_splice(self, expression):
        self._parse(expression.arg1)
        self._parse(expression.arg2)

    def _handle_item_modifier(self, expression):
        self._modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=self._get_domain(expression.arg1.arg2.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            src_attr=self._get_attribute(expression.arg2)
        ))

    def _handle_domain_modifier(self, expression):
        self._modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=self._get_domain(expression.arg1.arg2.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            src_attr=self._get_attribute(expression.arg2)
        ))

    def _handle_domain_group_modifier(self, expression):
        self._modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain_group,
            tgt_domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            tgt_filter_extra_arg=self._get_group(expression.arg1.arg2.arg1.arg2),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            src_attr=self._get_attribute(expression.arg2)
        ))

    def _handle_domain_skillrq_modifer(self, expression):
        self._modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain_skillrq,
            tgt_domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            tgt_filter_extra_arg=self._get_type(expression.arg1.arg2.arg1.arg2),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            src_attr=self._get_attribute(expression.arg2)
        ))

    def _handle_owner_skillrq_modifer(self, expression):
        self._modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.owner_skillrq,
            tgt_domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            tgt_filter_extra_arg=self._get_type(expression.arg1.arg2.arg1.arg2),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            src_attr=self._get_attribute(expression.arg2)
        ))

    def _get_domain(self, expression):
        if expression['operandID'] != Operand.def_dom:
            return None
        conversion_map = {
            'Self': ModifierDomain.self,
            'Char': ModifierDomain.character,
            'Ship': ModifierDomain.ship,
            'Target': ModifierDomain.target,
            'Other': ModifierDomain.other
        }
        return conversion_map[expression['expressionValue']]

    def _get_operator(self, expression):
        if expression['operandID'] != Operand.def_optr:
            return None
        conversion_map = {
            'PreAssignment': ModifierOperator.pre_assign,
            'PreMul': ModifierOperator.pre_mul,
            'PreDiv': ModifierOperator.pre_div,
            'ModAdd': ModifierOperator.mod_add,
            'ModSub': ModifierOperator.mod_sub,
            'PostMul': ModifierOperator.post_mul,
            'PostDiv': ModifierOperator.post_div,
            'PostPercent': ModifierOperator.post_percent,
            'PostAssignment': ModifierOperator.post_assign
        }
        return conversion_map[expression['expressionValue']]

    def _get_attribute(self, expression):
        if expression['operandID'] != Operand.def_attr:
            return None
        return int(expression['expressionAttributeID'])

    def _get_type(self, expression):
        operand = expression['operandID']
        if operand == Operand.def_type:
            return int(expression['expressionTypeID'])
        # Operand get_type specifies domain in its arg1;
        # typeID of this domain should be taken when needed
        elif operand == Operand.get_type:
            conversion_map = {
                ModifierDomain.self: EosType.current_self
            }
            domain = self._get_domain(expression.arg1)
            return conversion_map[domain]
        else:
            return None

    def _get_group(self, expression):
        if expression['operandID'] != Operand.def_grp:
            return None
        return int(expression['expressionGroupID'])

    def __prepare_expressions(self, expressions):
        # Convert regular dictionaries into custom
        # dictionaries for easier attribute access
        processed = {}
        for exp_row in expressions:
            processed[exp_row['expressionID']] = AttributeDict(exp_row)
        # Replace expression IDs in arg1/arg2 with
        # actual expressions
        for exp_row in processed.values():
            exp_row.arg1 = processed.get(exp_row['arg1'])
            exp_row.arg2 = processed.get(exp_row['arg2'])
        return processed
