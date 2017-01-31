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
from tests.calculator.environment import IndependentItem


class TestStateSwitching(CalculatorTestCase):
    """Test item state switching and modifier states"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1, stackable=1)
        src_attr1 = self.ch.attribute(attribute_id=2)
        src_attr2 = self.ch.attribute(attribute_id=3)
        src_attr3 = self.ch.attribute(attribute_id=4)
        src_attr4 = self.ch.attribute(attribute_id=5)
        src_attr5 = self.ch.attribute(attribute_id=6)
        modifier_off = DogmaModifier()
        modifier_off.state = State.offline
        modifier_off.tgt_filter = ModifierTargetFilter.item
        modifier_off.tgt_domain = ModifierDomain.self
        modifier_off.tgt_attr = self.tgt_attr.id
        modifier_off.operator = ModifierOperator.post_mul
        modifier_off.src_attr = src_attr1.id
        modifier_on = DogmaModifier()
        modifier_on.state = State.online
        modifier_on.tgt_filter = ModifierTargetFilter.item
        modifier_on.tgt_domain = ModifierDomain.self
        modifier_on.tgt_attr = self.tgt_attr.id
        modifier_on.operator = ModifierOperator.post_mul
        modifier_on.src_attr = src_attr2.id
        modifier_act = DogmaModifier()
        modifier_act.state = State.active
        modifier_act.tgt_filter = ModifierTargetFilter.item
        modifier_act.tgt_domain = ModifierDomain.self
        modifier_act.tgt_attr = self.tgt_attr.id
        modifier_act.operator = ModifierOperator.post_mul
        modifier_act.src_attr = src_attr3.id
        modifier_over = DogmaModifier()
        modifier_over.state = State.overload
        modifier_over.tgt_filter = ModifierTargetFilter.item
        modifier_over.tgt_domain = ModifierDomain.self
        modifier_over.tgt_attr = self.tgt_attr.id
        modifier_over.operator = ModifierOperator.post_mul
        modifier_over.src_attr = src_attr4.id
        modifier_disabled = DogmaModifier()
        modifier_disabled.state = State.active
        modifier_disabled.tgt_filter = ModifierTargetFilter.item
        modifier_disabled.tgt_domain = ModifierDomain.self
        modifier_disabled.tgt_attr = self.tgt_attr.id
        modifier_disabled.operator = ModifierOperator.post_mul
        modifier_disabled.src_attr = src_attr3.id
        # Overload category will make sure that item can enter all states
        effect = self.ch.effect(effect_id=1, category=EffectCategory.overload)
        effect.modifiers = (modifier_off, modifier_on, modifier_act, modifier_over)
        effect_disabled = self.ch.effect(effect_id=2, category=EffectCategory.active)
        effect_disabled.modifiers = (modifier_disabled,)
        self.item = IndependentItem(self.ch.type(
            type_id=1, effects=(effect, effect_disabled),
            attributes={
                self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3,
                src_attr3.id: 1.5, src_attr4.id: 1.7, src_attr5.id: 2
            }
        ))
        self.item._disabled_effects.add(effect_disabled.id)

    def test_fit_offline(self):
        # Setup
        self.item.state = State.offline
        # Action
        self.fit.items.add(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 110)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_fit_online(self):
        # Setup
        self.item.state = State.online
        # Action
        self.fit.items.add(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_fit_active(self):
        # Setup
        self.item.state = State.active
        # Action
        self.fit.items.add(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 214.5)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_fit_overloaded(self):
        # Setup
        self.item.state = State.overload
        # Action
        self.fit.items.add(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 364.65)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_up_single(self):
        # Setup
        self.item.state = State.offline
        self.fit.items.add(self.item)
        # Action
        self.item.state = State.online
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_up_multiple(self):
        # Setup
        self.item.state = State.online
        self.fit.items.add(self.item)
        # Action
        self.item.state = State.overload
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 364.65)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_down_single(self):
        # Setup
        self.item.state = State.overload
        self.fit.items.add(self.item)
        # Action
        self.item.state = State.active
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 214.5)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_down_multiple(self):
        # Setup
        self.item.state = State.active
        self.fit.items.add(self.item)
        # Action
        self.item.state = State.offline
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 110)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
