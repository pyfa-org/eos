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

from eos.const.eos import EffectBuildStatus, State, ModifierDomain, ModifierOperator, EosEveTypes
from eos.const.eve import EffectCategory, Operand
from eos.data.cache_object.modifier import *
from eos.util.attribute_dict import AttributeDict
from .exception import UnknownRootOperandError, UnknownPrimaryOperandError, UnexpectedHandlerError


logger = getLogger(__name__)


class ExpressionTree2Modifiers:
    """
    Class which uses effects' expression trees to generate
    actual modifier objects used by Eos.
    """

    def __init__(self, expressions):
        self._modifiers = None
        self._effect_category = None
        self.__expressions = self._prepare_expressions(expressions)

    def convert(self, effect_row):
        """Generate *Modifier objects for passed effect."""
        # Initialize instance attributes which
        # will be used during conversion
        self._modifiers = set()
        self._effect_category = effect_row['effect_category']
        # Run conversion
        try:
            self._parse(self.__expressions.get(effect_row['pre_expression']), root=True)
        # There're quite many root-level operands we do not
        # handle and do not want to handle. Special effects,
        # non-modifier definitions. Handle these somewhat
        # gracefully and mark such effects as skipped
        except UnknownRootOperandError as e:
            msg = 'failed to parse expression tree of effect {}: {}'.format(effect_row['effectID'], e.args[0])
            logger.info(msg)
            return (), EffectBuildStatus.skipped
        # Non-root level unknown operands and data inconsistencies
        # are reported as conversion errors
        except (UnknownPrimaryOperandError, UnexpectedHandlerError) as e:
            msg = 'failed to parse expression tree of effect {}: {}'.format(effect_row['effectID'], e.args[0])
            logger.error(msg)
            return (), EffectBuildStatus.error
        else:
            # Validation failures also reported as conversion errors
            for modifier in self._modifiers:
                if modifier._valid is not True:
                    msg = 'modifier of effect {} failed validation'.format(effect_row['effectID'])
                    logger.error(msg)
                    return (), EffectBuildStatus.error
            return self._modifiers, EffectBuildStatus.success

    def _handle_splice(self, expression):
        self._parse(expression.arg1)
        self._parse(expression.arg2)

    def _handle_add_itm_mod(self, expression):
        self._modifiers.add(ItemModifier(
            id_=None,
            domain=self._get_domain(expression.arg1.arg2.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2)
        ))

    def _handle_add_loc_mod(self, expression):
        self._modifiers.add(LocationModifier(
            id_=None,
            domain=self._get_domain(expression.arg1.arg2.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg2)
        ))

    def _handle_add_loc_grp_mod(self, expression):
        self._modifiers.add(LocationGroupModifier(
            id_=None,
            domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg1.arg2),
            group=self.__get_group(expression.arg2)
        ))

    def _handle_add_loc_srq_mod(self, expression):
        self._modifiers.add(LocationRequiredSkillModifier(
            id_=None,
            domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg1.arg2),
            skill=self._get_type(expression.arg2)
        ))

    def _handle_add_own_srq_mod(self, expression):
        self._modifiers.add(OwnerRequiredSkillModifier(
            id_=None,
            domain=self._get_domain(expression.arg1.arg2.arg1.arg1),
            state=self._get_state(),
            src_attr=self._get_attribute(expression.arg1.arg2.arg2),
            operator=self._get_operator(expression.arg1.arg1),
            tgt_attr=self._get_attribute(expression.arg1.arg2.arg1.arg2),
            skill=self._get_type(expression.arg2)
        ))

    _handler_map = {
        Operand.splice: _handle_splice,
        Operand.add_itm_mod: _handle_add_itm_mod,
        Operand.add_loc_mod: _handle_add_loc_mod,
        Operand.add_loc_grp_mod: _handle_add_loc_grp_mod,
        Operand.add_loc_srq_mod: _handle_add_loc_srq_mod,
        Operand.add_own_srq_mod: _handle_add_own_srq_mod
    }

    def _parse(self, expression, root=False):
        operand = expression.get('operandID')
        try:
            handler = self._handler_map[operand]
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
                raise UnexpectedHandlerError(msg) from e

    def _prepare_expressions(self, expressions):
        # Convert regular dictionaries into custom
        # dictionaries for easier attribute access
        processed = {}
        for exp_row in expressions:
            processed[exp_row['expressionID']] = AttributeDict(exp_row)
        # Replace expression IDs in arg1/arg2 with
        # actual expressions
        for exp_row in processed:
            exp_row.arg1 = processed.get(exp_row['arg1'])
            exp_row.arg2 = processed.get(exp_row['arg2'])
        return processed

    def _get_domain(self, expression):
        if expression['operandID'] != Operand.def_loc:
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

    def __get_group(self, expression):
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

    def _get_state(self):
        conversion_map = {
            EffectCategory.passive: State.offline,
            EffectCategory.active: State.active,
            EffectCategory.target: State.active,
            EffectCategory.online: State.online,
            EffectCategory.overload: State.overload,
            EffectCategory.system: State.offline
        }
        return conversion_map[self._effect_category]
