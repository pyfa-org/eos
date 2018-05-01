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


import logging
from unittest.mock import patch

from eos.const.eve import OperandId
from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


@patch('eos.eve_obj_builder.converter.ModBuilder')
class TestNormalizationIdzing(EveObjBuilderTestCase):
    """Check that conversion of symbolic references to IDs functions."""

    def get_log(self, name='eos.eve_obj_builder.normalizer'):
        return EveObjBuilderTestCase.get_log(self, name=name)

    def test_group_idzing(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append(
            {'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': OperandId.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'EnergyWeapon',
            'expressionTypeID': 567, 'expressionGroupID': None,
            'expressionAttributeID': 102})
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_builder()
        # Verification
        expressions = tuple(mod_builder.mock_calls[0][1][0])
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': OperandId.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': None, 'expressionTypeID': 567,
            'expressionGroupID': 53, 'expressionAttributeID': 102,
            'table_pos': 0}
        self.assertIn(expected, expressions)
        self.assert_log_entries(1)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.levelno, logging.WARNING)

    def test_group_ignorelist(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append(
            {'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': OperandId.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'PowerCore', 'expressionTypeID': 567,
            'expressionGroupID': None, 'expressionAttributeID': 102})
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_builder()
        # Verification
        expressions = tuple(mod_builder.mock_calls[0][1][0])
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': OperandId.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'PowerCore', 'expressionTypeID': 567,
            'expressionGroupID': None, 'expressionAttributeID': 102,
            'table_pos': 0}
        self.assertIn(expected, expressions)
        self.assert_log_entries(1)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.levelno, logging.WARNING)

    def test_warning_unused(self, mod_builder):
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_builder()
        # Verification
        self.assert_log_entries(1)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        self.assertEqual(
            idzing_stats.msg,
            '4 replacements for expressionGroupID were not used: '
            '"EnergyWeapon", "HybridWeapon", "MiningLaser", "ProjectileWeapon"')

    def test_warning_unknown(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append(
            {'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': OperandId.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'EnergyWeaponry',
            'expressionTypeID': 567, 'expressionGroupID': None,
            'expressionAttributeID': 102})
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_builder()
        # Verification
        self.assert_log_entries(2)
        idzing_stats_unused = self.log[0]
        self.assertEqual(idzing_stats_unused.levelno, logging.WARNING)
        idzing_stats_failures = self.log[1]
        self.assertEqual(idzing_stats_failures.levelno, logging.WARNING)
        self.assertEqual(
            idzing_stats_failures.msg,
            'unable to convert 1 literal references '
            'to expressionGroupID: "EnergyWeaponry"')
