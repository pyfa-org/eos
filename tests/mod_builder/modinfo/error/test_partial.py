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

from eos.const.eos import EffectBuildStatus
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from tests.mod_builder.testcase import ModBuilderTestCase


class TestBuilderModinfoErrorsPartial(ModBuilderTestCase):
    """Test that failures do not screw modbuilding process completely."""

    def test_error_func(self):
        effect_row = {
            'effectID': 1,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n- text\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.eve_obj_builder.mod_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg, 'effect 1, building 2 modifiers: 1 build errors')

    def test_no_func(self):
        effect_row = {
            'effectID': 1,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n'
                '- domain: charID\n  func: GangItemModifiero\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: 7\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.eve_obj_builder.mod_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg, 'effect 1, building 2 modifiers: 1 build errors')

    def test_error_unexpected_in_handler(self):
        effect_row = {
            'effectID': 22,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n'
                '- domain: charID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: ORE\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.eve_obj_builder.mod_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg, 'effect 22, building 2 modifiers: 1 build errors')

    def test_validation_failure(self):
        effect_row = {
            'effectID': 1,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n'
                '- domain: shipID\n  func: OwnerRequiredSkillModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: 6\n  skillTypeID: 55\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.eve_obj_builder.mod_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg,
            'effect 1, building 2 modifiers: 1 validation failures')

    def test_building_and_validation_failure(self):
        effect_row = {
            'effectID': 1,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n'
                '- domain: shipID\n  func: OwnerRequiredSkillModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: 6\n  skillTypeID: 55\n'
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: ORE\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.eve_obj_builder.mod_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg,
            'effect 1, building 3 modifiers: '
            '1 build errors, 1 validation failures')

    def test_error_before(self):
        effect_row = {
            'effectID': 94,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier22\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n'
                '- domain: charID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: 7\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModTgtFilter.item)
        self.assertEqual(modifier.tgt_domain, ModDomain.character)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr_id, 33)
        self.assertEqual(modifier.operator, ModOperator.post_assign)
        self.assertEqual(modifier.src_attr_id, 44)
        # Unknown function error, tested separately
        self.assertEqual(len(self.get_log()), 1)

    def test_error_after(self):
        effect_row = {
            'effectID': 94,
            'modifierInfo':
                '- domain: shipID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n'
                '  operator: 6\n'
                '- domain: charID\n  func: ItemModifier22\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n'
                '  operator: 7\n'}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModTgtFilter.item)
        self.assertEqual(modifier.tgt_domain, ModDomain.ship)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr_id, 22)
        self.assertEqual(modifier.operator, ModOperator.post_percent)
        self.assertEqual(modifier.src_attr_id, 11)
        # Unknown function error, tested separately
        self.assertEqual(len(self.get_log()), 1)
