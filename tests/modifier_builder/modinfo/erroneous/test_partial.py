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

from eos.const.eos import State, Domain, EffectBuildStatus, Scope, Operator
from eos.const.eve import EffectCategory
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderModinfoErrorsPartial(ModBuilderTestCase):
    """
    Test errors occurring during different stages of dealing with modifier info,
    in this class they do not let to finish conversion on per-modifier basis.
    """

    def test_error_func(self):
        effect_row = {
            'effect_id': 1,
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: charID\n  func: GangItemModifiero\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 7\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.WARNING)
        expected = 'failed to build one of the modifiers of effect 1: unknown filter function GangItemModifiero'
        self.assertEqual(log_record.msg, expected)

    def test_error_filter_value(self):
        effect_row = {
            'effect_id': 1,
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: charID\n  func: LocationGroupModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 7\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.WARNING)
        expected = ('failed to build one of the modifiers of effect 1: unable to find '
            'attribute groupID for filter value')
        self.assertEqual(log_record.msg, expected)

    def test_error_domain(self):
        effect_row = {
            'effect_id': 58,
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: targetID\n  func: GangItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 7\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.WARNING)
        expected = ('failed to build one of the modifiers of effect 58: unexpected domain targetID'
            ' for filter function GangItemModifier')
        self.assertEqual(log_record.msg, expected)

    def test_error_operator(self):
        effect_row = {
            'effect_id': 36,
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: charID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 99\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.modifier_info.info2modifiers')
        self.assertEqual(log_record.levelno, logging.WARNING)
        expected = 'failed to build one of the modifiers of effect 36: unknown operator 99'
        self.assertEqual(log_record.msg, expected)

    def test_error_before(self):
        effect_row = {
            'effect_id': 94,
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier22\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: charID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 7\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(modifier.domain, Domain.character)
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.src_attr, 44)
        self.assertEqual(modifier.operator, Operator.post_assign)
        self.assertEqual(modifier.tgt_attr, 33)
        self.assertIsNone(modifier.filter_type)
        self.assertIsNone(modifier.filter_value)
        self.assertEqual(len(self.log), 1)

    def test_error_after(self):
        effect_row = {
            'effect_id': 94,
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: charID\n  func: ItemModifier22\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 7\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(modifier.domain, Domain.ship)
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.src_attr, 11)
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(modifier.tgt_attr, 22)
        self.assertIsNone(modifier.filter_type)
        self.assertIsNone(modifier.filter_value)
        self.assertEqual(len(self.log), 1)
