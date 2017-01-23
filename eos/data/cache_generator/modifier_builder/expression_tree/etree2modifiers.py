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


from logging import getLogger

from eos.const.eos import EffectBuildStatus, ModifierType, ModifierDomain, ModifierOperator, EosEveTypes
from eos.const.eve import Operand
from eos.data.cache_object import Modifier
from eos.util.attribute_dict import AttributeDict
from .exception import *
from ..shared import STATE_CONVERSION_MAP


logger = getLogger(__name__)


class ExpressionTree2Modifiers:
    """
    Class which uses effects' expression trees to generate
    actual modifier objects used by Eos.
    """

    def __init__(self, expressions):
        self._modifiers = None
        self._effect_category = None
        self.__expressions = self.__prepare_expressions(expressions)

    def convert(self, effect_row):
        """Generate *Modifier objects for passed effect."""
        # Initialize instance attributes which
        # will be used during conversion
        self._modifiers = set()
        self._effect_category = effect_row['effect_category']
        # Run conversion
        root_expression = self.__expressions.get(effect_row['pre_expression'])
        try:
            self._parse(root_expression, root=True)
        # There're quite many root-level operands we do not
        # handle and do not want to handle. Special effects,
        # non-modifier definitions. Handle these somewhat
        # gracefully and mark such effects as skipped
        except UnknownRootOperandError as e:
            effect_id = effect_row['effect_id']
            msg = 'failed to parse effect {}: {}'.format(effect_id, e.args[0])
            logger.info(msg)
            return (), EffectBuildStatus.skipped
        # Non-root level unknown operands and data inconsistencies
        # are reported as conversion errors
        except (UnknownPrimaryOperandError, UnexpectedHandlingError) as e:
            effect_id = effect_row['effect_id']
            msg = 'failed to parse effect {}: {}'.format(effect_id, e.args[0])
            logger.error(msg)
            return (), EffectBuildStatus.error
        # Validation failures are reported as partial success or
        # conversion errors, depending on amount of valid modifiers
        else:
            valid_modifiers = set()
            validation_failures = 0
            for modifier in self._modifiers:
                if modifier._valid is True:
                    valid_modifiers.add(modifier)
                else:
                    validation_failures += 1
            if validation_failures == 0:
                return valid_modifiers, EffectBuildStatus.success_full
            else:
                effect_id = effect_row['effect_id']
                plural = 's' if validation_failures > 1 else ''
                msg = '{} modifier{} of effect {} failed validation'.format(validation_failures, plural, effect_id)
                logger.error(msg)
                if len(valid_modifiers) > 0:
                    return valid_modifiers, EffectBuildStatus.success_partial
                else:
                    return (), EffectBuildStatus.error

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
                raise UnknownRootOperandError(msg) from e
            else:
                msg = 'unknown non-root primary operand {}'.format(operand)
                raise UnknownPrimaryOperandError(msg) from e
        else:
            try:
                handler(expression)
            # Propagate exceptions which we want to report to the caller,
            # and which may be raised in non-root calls
            except (KeyboardInterrupt, UnknownRootOperandError, UnknownPrimaryOperandError):
                raise
            except Exception as e:
                msg = 'unexpected error in handler'
                raise UnexpectedHandlingError(msg) from e

    def _handle_splice(self, expression):
        self._parse(expression.arg1)
        self._parse(expression.arg2)

    def _handle_item_modifier(self, expression):
        self._modifiers.add(Modifier(
            modifier_type=ModifierType.item,
            domain=self._get_domain(expression.arg1.arg2.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2)
        ))

    def _handle_domain_modifier(self, expression):
        self._modifiers.add(Modifier(
            modifier_type=ModifierType.domain,
            domain=self._get_domain(expression.arg1.arg2.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2)
        ))

    def _handle_domain_group_modifier(self, expression):
        self._modifiers.add(Modifier(
            modifier_type=ModifierType.domain_group,
            domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            extra_arg=self._get_group(expression.arg1.arg2.arg1.arg2)
        ))

    def _handle_domain_skillrq_modifer(self, expression):
        self._modifiers.add(Modifier(
            modifier_type=ModifierType.domain_skillrq,
            domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            extra_arg=self._get_type(expression.arg1.arg2.arg1.arg2)
        ))

    def _handle_owner_skillrq_modifer(self, expression):
        self._modifiers.add(Modifier(
            modifier_type=ModifierType.owner_skillrq,
            domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2),
            extra_arg=self._get_type(expression.arg1.arg2.arg1.arg2)
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

    def _get_state(self):
        return STATE_CONVERSION_MAP[self._effect_category]

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

    def _get_group(self, expression):
        if expression['operandID'] != Operand.def_grp:
            return None
        return int(expression['expressionGroupID'])

    def _get_type(self, expression):
        operand = expression['operandID']
        if operand == Operand.def_type:
            return int(expression['expressionTypeID'])
        # Operand get_type specifies domain in its arg1;
        # typeID of this domain should be taken when needed
        elif operand == Operand.get_type:
            conversion_map = {
                ModifierDomain.self: EosEveTypes.current_self
            }
            domain = self._get_domain(expression.arg1)
            return conversion_map[domain]
        else:
            return None

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
