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


import logging
from unittest.mock import patch

from eos.const.eve import Operand
from tests.cache_generator.generator_testcase import GeneratorTestCase


@patch('eos.data.cache_generator.converter.ModifierBuilder')
class TestNormalizationIdzing(GeneratorTestCase):
    """Check that conversion of symbolic references to IDs functions."""

    def test_group_idzing(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'EnergyWeapon', 'expressionTypeID': 567,
            'expressionGroupID': None, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_generator()
        # Verification
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007, 'arg2': 66,
            'expressionValue': None, 'expressionTypeID': 567, 'expressionGroupID': 53,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)

    def test_group_ignorelist(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'PowerCore', 'expressionTypeID': 567,
            'expressionGroupID': None, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_generator()
        # Verification
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007, 'arg2': 66,
            'expressionValue': 'PowerCore', 'expressionTypeID': 567, 'expressionGroupID': None,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)

    def test_warning_unused(self, mod_builder):
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_generator()
        # Verification
        self.assertEqual(len(self.log), 1)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        self.assertEqual(
            idzing_stats.msg, '4 replacements for expressionGroupID were not used: '
            '"EnergyWeapon", "HybridWeapon", "MiningLaser", "ProjectileWeapon"'
        )

    def test_warning_unknown(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'EnergyWeaponry', 'expressionTypeID': 567,
            'expressionGroupID': None, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        # Action
        self.run_generator()
        # Verification
        self.assertEqual(len(self.log), 3)
        idzing_stats_unused = self.log[0]
        self.assertEqual(idzing_stats_unused.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats_unused.levelno, logging.WARNING)
        idzing_stats_failures = self.log[1]
        self.assertEqual(idzing_stats_failures.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats_failures.levelno, logging.WARNING)
        self.assertEqual(
            idzing_stats_failures.msg, 'unable to convert 1 literal references '
            'to expressionGroupID: "EnergyWeaponry"'
        )
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
