# ==============================================================================
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
# ==============================================================================


import logging
from unittest.mock import patch

from tests.eve_obj_builder.eve_obj_builder_testcase import EveObjBuilderTestCase


class TestConversionExpression(EveObjBuilderTestCase):
    """Check form of expression rows passed to modifier builder."""

    logger_name = 'eos.data.eve_obj_builder.converter'

    @patch('eos.data.eve_obj_builder.converter.ModifierBuilder')
    def test_fields(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append(
            {'effectID': 111, 'preExpression': 57, 'postExpression': 41})
        self.dh.data['dgmexpressions'].append({
            'expressionTypeID': 502, 'expressionValue': None,
            'randomField': 'vals', 'operandID': 6, 'arg1': 1009,
            'expressionID': 41, 'arg2': 15, 'expressionAttributeID': 90,
            'expressionGroupID': 451})
        self.dh.data['dgmexpressions'].append({
            'expressionGroupID': 567, 'arg2': 66, 'operandID': 33, 'arg1': 5007,
            'expressionID': 57, 'expressionTypeID': 551, 'randoom': True,
            'expressionAttributeID': 102, 'expressionValue': 'Kurr'})
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_builder()
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 0)
        # As expressions are absent in final container, check those which were
        # passed to modifier builder
        expressions = tuple(mod_builder.mock_calls[0][1][0])
        self.assertEqual(len(expressions), 2)
        # It's fine that additional fields get into final expression set,
        # because they will be replaced by modifiers anyway
        expected = {
            'expressionID': 41, 'operandID': 6, 'arg1': 1009, 'arg2': 15,
            'expressionValue': None, 'expressionTypeID': 502,
            'expressionGroupID': 451, 'expressionAttributeID': 90,
            'table_pos': 0, 'randomField': 'vals'}
        self.assertIn(expected, expressions)
        expected = {
            'expressionID': 57, 'operandID': 33, 'arg1': 5007, 'arg2': 66,
            'expressionValue': 'Kurr', 'expressionTypeID': 551,
            'expressionGroupID': 567, 'expressionAttributeID': 102,
            'table_pos': 1, 'randoom': True}
        self.assertIn(expected, expressions)
