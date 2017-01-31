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


from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.fit.calculator.modifier import DogmaModifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import ChargeItem, ContainerItem, IndependentItem


class TestTgtItemDomainOther(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        self.src_attr = self.ch.attribute(attribute_id=2)
        modifier = DogmaModifier()
        modifier.state = State.offline
        modifier.tgt_filter = ModifierTargetFilter.item
        modifier.tgt_domain = ModifierDomain.other
        modifier.tgt_attr = self.tgt_attr.id
        modifier.operator = ModifierOperator.post_percent
        modifier.src_attr = self.src_attr.id
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_other_domain_container(self):
        influence_source = ContainerItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.src_attr.id: 20}
        ))
        influence_target = ChargeItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        # Action
        influence_source.charge = influence_target
        influence_target.container = influence_source
        self.fit.items.add(influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.items.remove(influence_source)
        influence_source.charge = None
        influence_target.container = None
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_other_domain_charge(self):
        influence_source = ChargeItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.src_attr.id: 20}
        ))
        influence_target = ContainerItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        # Action
        influence_source.container = influence_target
        influence_target.charge = influence_source
        self.fit.items.add(influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.items.remove(influence_source)
        influence_source.container = None
        influence_target.charge = None
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_self(self):
        # Check that source item isn't modified
        influence_source = ContainerItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        ))
        influence_target = ChargeItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        # Action
        influence_source.charge = influence_target
        influence_target.container = influence_source
        self.fit.items.add(influence_source)
        # Verification
        self.assertAlmostEqual(influence_source.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(influence_target)
        influence_source.charge = None
        influence_target.container = None
        self.fit.items.remove(influence_source)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_other_item(self):
        # Here we check some "random" item, w/o linking items
        influence_source = ContainerItem(self.ch.type(
            type_id=1, effects=(self.effect,),
            attributes={self.src_attr.id: 20}
        ))
        influence_target = IndependentItem(self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        # Action
        self.fit.items.add(influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(influence_source)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
