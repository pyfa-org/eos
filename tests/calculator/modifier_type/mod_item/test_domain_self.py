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


from eos.const.eos import ModifierType, ModifierDomain, ModifierOperator, State
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, CharDomainItem, ShipDomainItem


class TestModItemDomainSelf(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        self.src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.type = ModifierType.item
        modifier.domain = ModifierDomain.self
        modifier.state = State.offline
        modifier.src_attr = self.src_attr.id
        modifier.operator = ModifierOperator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_independent(self):
        item = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_character(self):
        item = CharDomainItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_ship(self):
        item = ShipDomainItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_positioned(self):
        item = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        ))
        # Action
        self.fit.character = item
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.character = None
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_other(self):
        # Here we check that self-reference modifies only carrier of effect,
        # and nothing else is affected. We position item as character and
        # check another item which has character modifier domain to ensure
        # that items 'belonging' to self are not affected too
        influence_source = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        ))
        item = CharDomainItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(item)
        # Action
        self.fit.character = influence_source
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.character = None
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
