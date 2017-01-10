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


from eos.const.eos import State, Domain, Scope, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestStateSwitching(CalculatorTestCase):
    """Test holder state switching and modifier states"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1, stackable=1)
        src_attr1 = self.ch.attribute(attribute_id=2)
        src_attr2 = self.ch.attribute(attribute_id=3)
        src_attr3 = self.ch.attribute(attribute_id=4)
        src_attr4 = self.ch.attribute(attribute_id=5)
        src_attr5 = self.ch.attribute(attribute_id=6)
        modifier_off = Modifier()
        modifier_off.state = State.offline
        modifier_off.scope = Scope.local
        modifier_off.src_attr = src_attr1.id
        modifier_off.operator = Operator.post_mul
        modifier_off.tgt_attr = self.tgt_attr.id
        modifier_off.domain = Domain.self_
        modifier_off.filter_type = None
        modifier_off.filter_value = None
        modifier_on = Modifier()
        modifier_on.state = State.online
        modifier_on.scope = Scope.local
        modifier_on.src_attr = src_attr2.id
        modifier_on.operator = Operator.post_mul
        modifier_on.tgt_attr = self.tgt_attr.id
        modifier_on.domain = Domain.self_
        modifier_on.filter_type = None
        modifier_on.filter_value = None
        modifier_act = Modifier()
        modifier_act.state = State.active
        modifier_act.scope = Scope.local
        modifier_act.src_attr = src_attr3.id
        modifier_act.operator = Operator.post_mul
        modifier_act.tgt_attr = self.tgt_attr.id
        modifier_act.domain = Domain.self_
        modifier_act.filter_type = None
        modifier_act.filter_value = None
        modifier_over = Modifier()
        modifier_over.state = State.overload
        modifier_over.scope = Scope.local
        modifier_over.src_attr = src_attr4.id
        modifier_over.operator = Operator.post_mul
        modifier_over.tgt_attr = self.tgt_attr.id
        modifier_over.domain = Domain.self_
        modifier_over.filter_type = None
        modifier_over.filter_value = None
        modifier_separate = Modifier()
        modifier_separate.state = State.active
        modifier_separate.scope = Scope.local
        modifier_separate.src_attr = src_attr3.id
        modifier_separate.operator = Operator.post_mul
        modifier_separate.tgt_attr = self.tgt_attr.id
        modifier_separate.domain = Domain.self_
        modifier_separate.filter_type = None
        modifier_separate.filter_value = None
        # Overload category will make sure that holder can enter all states
        effect1 = self.ch.effect(effect_id=1, category=EffectCategory.overload)
        effect1.modifiers = (modifier_off, modifier_on, modifier_act, modifier_over)
        effect2 = self.ch.effect(effect_id=2, category=EffectCategory.active)
        effect2.modifiers = (modifier_separate,)
        self.holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(effect1, effect2),
            attributes={
                self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3,
                src_attr3.id: 1.5, src_attr4.id: 1.7, src_attr5.id: 2
            }
        ))
        self.holder._disabled_effects.add(effect2.id)

    def test_fit_offline(self):
        # Setup
        self.holder.state = State.offline
        # Action
        self.fit.items.add(self.holder)
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 110)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_fit_online(self):
        # Setup
        self.holder.state = State.online
        # Action
        self.fit.items.add(self.holder)
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_fit_active(self):
        # Setup
        self.holder.state = State.active
        # Action
        self.fit.items.add(self.holder)
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 214.5)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_fit_overloaded(self):
        # Setup
        self.holder.state = State.overload
        # Action
        self.fit.items.add(self.holder)
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 364.65)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_up_single(self):
        # Setup
        self.holder.state = State.offline
        self.fit.items.add(self.holder)
        # Action
        self.holder.state = State.online
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_up_multiple(self):
        # Setup
        self.holder.state = State.online
        self.fit.items.add(self.holder)
        # Action
        self.holder.state = State.overload
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 364.65)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_down_single(self):
        # Setup
        self.holder.state = State.overload
        self.fit.items.add(self.holder)
        # Action
        self.holder.state = State.active
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 214.5)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_switch_down_multiple(self):
        # Setup
        self.holder.state = State.active
        self.fit.items.add(self.holder)
        # Action
        self.holder.state = State.offline
        # Verification
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 110)
        # Cleanup
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
