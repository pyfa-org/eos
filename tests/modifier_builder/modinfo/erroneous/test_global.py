# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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

from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderModinfoErrorsGlobal(ModBuilderTestCase):
    """
    Test errors occurring during different stages of dealing with modifier info,
    in this class they screw conversion process altogether.
    """

    def test_error_yaml(self):
        effect_row = {
            'effect_id': 94,
            'effect_category': EffectCategory.passive,
            'modifier_info': 'yap((EWH\x02'
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'failed to parse modifier info YAML for effect 94'
        self.assertEqual(log_record.msg, expected)

    def test_error_state(self):
        effect_row = {
            'effect_id': 36,
            'effect_category': 99,
            'modifier_info': '- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n'
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.WARNING)
        expected = 'failed to build modifiers for effect 36: cannot convert effect category 99 into state'
        self.assertEqual(log_record.msg, expected)

    def test_error_unknown(self):
        # Here we just use YAML which contains list with single None item
        # instead of what we usually expect
        effect_row = {
            'effect_id': 22,
            'effect_category': EffectCategory.passive,
            'modifier_info': '-'
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'failed to build modifiers for effect 22 due to unknown reason'
        self.assertEqual(log_record.msg, expected)
