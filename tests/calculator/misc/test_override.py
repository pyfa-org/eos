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
from eos.data.cache_object.modifier import DogmaModifier
from eos.fit.messages import AttrValueChanged, AttrValueChangedMasked
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
        modifier1 = DogmaModifier()
        modifier1.state = State.online
        modifier1.tgt_filter = ModifierTargetFilter.item
        modifier1.tgt_domain = ModifierDomain.self
        modifier1.tgt_attr = self.attr2.id
        modifier1.operator = ModifierOperator.post_percent
        modifier1.src_attr = self.attr1.id
        modifier2 = DogmaModifier()
        modifier2.state = State.offline
        modifier2.tgt_filter = ModifierTargetFilter.item
        modifier2.tgt_domain = ModifierDomain.self
        modifier2.tgt_attr = self.attr3.id
        modifier2.operator = ModifierOperator.post_percent
        modifier2.src_attr = self.attr2.id
        modifier3 = DogmaModifier()
        modifier3.state = State.offline
        modifier3.tgt_filter = ModifierTargetFilter.item
        modifier3.tgt_domain = ModifierDomain.self
        modifier3.tgt_attr = self.attr4.id
        modifier3.operator = ModifierOperator.post_percent
        modifier3.src_attr = self.attr3.id
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier1, modifier2, modifier3)
        self.item = IndependentItem(self.ch.type(
            type_id=1, effects=(effect,),
            attributes={self.attr1.id: 50, self.attr2.id: 100, self.attr3.id: 5, self.attr4.id: 50}
        ))
        self.fit = Fit(self.ch, msgstore_filter=lambda m: isinstance(m, (AttrValueChanged, AttrValueChangedMasked)))
        self.fit.items.add(self.item)

    def test_override_set(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr4.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._set_override_callback(self.attr3.id, (lambda x, y, z: x - y + z, (55,), {'y': 11, 'z': 33}))
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._set_override_callback(self.attr3.id, (lambda: 88, (), {}))
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 88)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 94)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset_unchanged(self):
        # Setup

        def callback_func(x, y=0):
            return x + y

        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (callback_func, (66,), {'y': 11}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._set_override_callback(self.attr3.id, (callback_func, (66,), {'y': 11}))
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_changed_via_parent_regular_update(self):
        # Setup
        item = self.item
        # Force fetching attribute to make sure it's stored in
        # dictionary of modified attributes
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        # Force change of attribute which affects overridden attr3 only
        # after attr3 override has been set. This way we're checking
        # that after override is deleted, value is properly refreshed
        item.state = State.online
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._del_override_callback(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 12.5)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 56.25)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_changed_via_parent_override(self):
        # Setup
        item = self.item
        # Force fetching attribute to make sure it's stored in
        # dictionary of modified attributes
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        # Force change of attribute which affects overridden attr3 only
        # after attr3 override has been set. This way we're checking
        # that after override is deleted, value is properly refreshed
        item.attributes._set_override_callback(self.attr2.id, (lambda: 200, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._del_override_callback(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 15)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 57.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_persistence_delete(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        del item.attributes[self.attr3.id]
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_persistence_clear(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_ignore(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        messages_before = len(self.fit.message_store)
        # Action
        self.assertAlmostEqual(item.attributes._get_without_overrides(self.attr3.id), 10)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = self.fit.message_store[-2]
        self.assertTrue(isinstance(message1, AttrValueChanged))
        self.assertIs(message1.item, self.item)
        self.assertEqual(message1.attr, self.attr3.id)
        message2 = self.fit.message_store[-1]
        self.assertTrue(isinstance(message2, AttrValueChanged))
        self.assertIs(message2.item, self.item)
        self.assertEqual(message2.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_chain_damaging_override(self):
        # Here we make sure that when damaging of attribute
        # tree is initiated, it's stopped on override
        # Setup
        item = self.item
        fit = Fit(self.ch, msgstore_filter=lambda m: isinstance(m, (AttrValueChanged, AttrValueChangedMasked)))
        fit.items.add(item)
        # Force fetching attribute to make sure it's stored in
        # dictionary of modified attributes
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        messages_before = len(fit.message_store)
        # Action
        item.state = State.online
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.item, self.item)
        # Only attr2 has been changed as attr3 is overriden. Calculator
        # doesn't receive any messages about changed value of attr3
        self.assertEqual(message.attr, self.attr2.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_notification_changing(self):
        # Setup
        item = self.item
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._override_value_may_change(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChanged))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_calculator_buffers_empty(self.fit)
