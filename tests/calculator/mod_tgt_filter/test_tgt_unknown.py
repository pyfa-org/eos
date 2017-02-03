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

from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestTgtFilterUnknown(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = tgt_attr = self.ch.attribute(attribute_id=1)
        self.src_attr = src_attr = self.ch.attribute(attribute_id=2)
        self.invalid_modifier = invalid_modifier = DogmaModifier()
        invalid_modifier.tgt_filter = 26500
        invalid_modifier.tgt_domain = ModifierDomain.self
        invalid_modifier.state = State.offline
        invalid_modifier.src_attr = src_attr.id
        invalid_modifier.operator = ModifierOperator.post_percent
        invalid_modifier.tgt_attr = tgt_attr.id
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)

    def test_log(self):
        self.effect.modifiers = (self.invalid_modifier,)
        item = IndependentItem(self.ch.type(
            type_id=31, effects=(self.effect,),
            attributes={self.src_attr.id: 20, self.tgt_attr: 100}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        self.assertEqual(len(self.log), 2)
        for log_record in self.log:
            self.assertEqual(log_record.name, 'eos.fit.calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(log_record.msg, 'malformed modifier on eve type 31: invalid target filter 26500')
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_combination(self):
        valid_modifier = DogmaModifier()
        valid_modifier.tgt_filter = ModifierTargetFilter.item
        valid_modifier.tgt_domain = ModifierDomain.self
        valid_modifier.state = State.offline
        valid_modifier.src_attr = self.src_attr.id
        valid_modifier.operator = ModifierOperator.post_percent
        valid_modifier.tgt_attr = self.tgt_attr.id
        self.effect.modifiers = (self.invalid_modifier, valid_modifier)
        item = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.src_attr.id: 20, self.tgt_attr.id: 100}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        # Invalid filter type in modifier should prevent proper processing of other modifiers
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 5)
        self.assert_calculator_buffers_empty(self.fit)
