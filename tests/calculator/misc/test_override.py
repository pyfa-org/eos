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


from eos.const.eos import State, Domain, Scope, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from eos.fit.messages import AttrValueChanged, AttrValueChangedOverride
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import Fit, IndependentItem


class TestOverride(CalculatorTestCase):
    """
    Check that attribute overriding functions as expected.
    """

    def setUp(self):
        super().setUp()
        self.attr1 = self.ch.attribute(attribute_id=1)
        self.attr2 = self.ch.attribute(attribute_id=2)
        self.attr3 = self.ch.attribute(attribute_id=3)
        self.attr4 = self.ch.attribute(attribute_id=4)
        modifier1 = Modifier()
        modifier1.state = State.online
        modifier1.scope = Scope.local
        modifier1.src_attr = self.attr1.id
        modifier1.operator = Operator.post_percent
        modifier1.tgt_attr = self.attr2.id
        modifier1.domain = Domain.self_
        modifier1.filter_type = None
        modifier1.filter_value = None
        modifier2 = Modifier()
        modifier2.state = State.offline
        modifier2.scope = Scope.local
        modifier2.src_attr = self.attr2.id
        modifier2.operator = Operator.post_percent
        modifier2.tgt_attr = self.attr3.id
        modifier2.domain = Domain.self_
        modifier2.filter_type = None
        modifier2.filter_value = None
        modifier3 = Modifier()
        modifier3.state = State.offline
        modifier3.scope = Scope.local
        modifier3.src_attr = self.attr3.id
        modifier3.operator = Operator.post_percent
        modifier3.tgt_attr = self.attr4.id
        modifier3.domain = Domain.self_
        modifier3.filter_type = None
        modifier3.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier1, modifier2, modifier3)
        self.holder = IndependentItem(self.ch.type_(type_id=1, effects=(effect,),
            attributes={self.attr1.id: 50, self.attr2.id: 100, self.attr3.id: 5, self.attr4.id: 50}))
        self.fit = Fit(self.ch, msgstore_filter=lambda m: isinstance(m, AttrValueChangedOverride))
        self.fit.items.add(self.holder)

    def test_override_set(self):
        # Setup
        holder = self.holder
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr3.id, 77)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedOverride))
        self.assertIs(message.holder, self.holder)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_set_unchanged(self):
        # Setup
        holder = self.holder
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr3.id, 10)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr3.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr3.id, 88)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedOverride))
        self.assertIs(message.holder, self.holder)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 94)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset_unchanged(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr3.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr3.id, 77)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_changed_via_parent_regular_update(self):
        # Setup
        holder = self.holder
        # Force fetching attribute to make sure it's stored in
        # dictionary of modified attributes
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 10)
        holder.attributes._override_set(self.attr3.id, 77)
        # Force change of attribute which affects overridden attr3 only
        # after attr3 override has been set. This way we're checking
        # that after override is deleted, value is properly refreshed
        holder.state = State.online
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_del(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedOverride))
        self.assertIs(message.holder, self.holder)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 12.5)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 56.25)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_changed_via_parent_override(self):
        # Setup
        holder = self.holder
        # Force fetching attribute to make sure it's stored in
        # dictionary of modified attributes
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 10)
        holder.attributes._override_set(self.attr3.id, 77)
        # Force change of attribute which affects overridden attr3 only
        # after attr3 override has been set. This way we're checking
        # that after override is deleted, value is properly refreshed
        holder.attributes._override_set(self.attr2.id, 200)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_del(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedOverride))
        self.assertIs(message.holder, self.holder)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 15)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 57.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_persistent(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr3.id, 77, persist=True)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_del(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedOverride))
        self.assertIs(message.holder, self.holder)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_clear(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr3.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedOverride))
        self.assertIs(message.holder, self.holder)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_clear_persistent(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr3.id, 77, persist=True)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_chain_damaging_override(self):
        # Here we make sure that when damaging of attribute
        # tree is initiated, it's stopped on override
        # Setup
        holder = self.holder
        fit = Fit(self.ch, msgstore_filter=lambda m: isinstance(m, (AttrValueChanged, AttrValueChangedOverride)))
        fit.items.add(holder)
        # Force fetching attribute to make sure it's stored in
        # dictionary of modified attributes
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 10)
        holder.attributes._override_set(self.attr3.id, 77)
        messages_before = len(fit.message_store)
        # Action
        holder.state = State.online
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.holder, self.holder)
        # Only attr2 has been changed as attr3 is overriden. Calculator
        # doesn't receive any messages about changed value of attr3
        self.assertEqual(message.attr, self.attr2.id)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)
