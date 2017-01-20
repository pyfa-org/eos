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


from eos.const.eve import Operand
from .exception import ExpressionFetchError




class Effect2Modifiers:
    """
    Class which uses effects' expression trees to generate
    actual modifier objects used by Eos.
    """

    def __init__(self, expressions):
        self._expressions = self.__prepare_expressions(expressions)

    def convert(self, effect_row):
        """Generate Modifier objects out of passed data."""
        self.modifiers = []
        self.effect_category_id = effect_row['effect_category']
        pre_expression_id = effect_row['pre_expression']
        self._parse(pre_expression_id)

    def _handle_splice(self, expression):
        self._parse(self.__get_exp(expression.get('arg1')))
        self._parse(self.__get_exp(expression.get('arg2')))

    def _handle_add_itm_mod(self, expression):
        pass

    def _handle_add_loc_mod(self, expression):
        pass

    def _handle_add_loc_grp_mod(self, expression):
        pass

    def _handle_add_loc_srq_mod(self, expression):
        pass

    def _handle_add_own_srq_mod(self, expression):
        pass

    _handler_map = {
        Operand.splice: _handle_splice,
        Operand.add_itm_mod: None,
        Operand.add_loc_mod: None,
        Operand.add_loc_grp_mod: None,
        Operand.add_loc_srq_mod: None,
        Operand.add_own_srq_mod: None
    }

    def _parse(self, expression):
        operand_id = expression.get('operandID')
        try:
            handler = self._handler_map[operand_id]
        except KeyboardInterrupt:
            raise
        except:
            # TODO: do something here? E.g. set status of effect and
            # make few log entries
            pass
        else:
            handler(expression)

    def __prepare_expressions(self, expressions):
        processed = {}
        for exp_row in expressions:
            processed[exp_row['expressionID']] = exp_row
        return processed

    def __get_exp(self, expression_id):
        try:
            return self._expressions[expression_id]
        except KeyError as e:
            msg = 'unable to fetch expression {}'.format(expression_id)
            raise ExpressionFetchError(msg) from e

    def __get_operator(self, expression):
        conversion_map = {
            'PreAssignment': Operator.pre_assign,
            'PreMul': Operator.pre_mul,
            'PreDiv': Operator.pre_div,
            'ModAdd': Operator.mod_add,
            'ModSub': Operator.mod_sub,
            'PostMul': Operator.post_mul,
            'PostDiv': Operator.post_div,
            'PostPercent': Operator.post_percent,
            'PostAssignment': Operator.post_assign
        }
        operator = conversion_map[expression.get('expressionValue')]
        return operator

    def __get_domain(self, expression):
        # Format: {eve location name: eos domain ID}
        conversion_map = {
            'Self': Domain.self,
            'Char': Domain.character,
            'Ship': Domain.ship,
            'Target': Domain.target,
            'Other': Domain.other,
            'Area': Domain.area
        }
        domain = conversion_map[expression.get('expressionValue')]
        return domain

    def __get_attribute(self, expression):
        attribute = int(expression.get('expressionAttributeID'))
        return attribute

    def __get_group(self, expression):
        group = int(expression.get('expressionGroupID'))
        return group

    def __get_type(self, expression, action):
        # Type getter function has special handling
        if expression.get('operandID') == Operand.get_type:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            arg1 = self._get_exp(expression.get('arg1'))
            if self._get_domain(arg1) == Domain.self:
                action.tgt_skillrq_self = True
        else:
            action.tgt_skillrq = int(expression.get('expressionTypeID'))
