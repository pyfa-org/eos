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
from eos.fit.messages import AttrValueChangedOverride
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
        modifier1 = Modifier()
        modifier1.state = State.offline
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
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier1, modifier2)
        self.holder = IndependentItem(self.ch.type_(type_id=1, effects=(effect,),
            attributes={self.attr1.id: 100, self.attr2.id: 5, self.attr3.id: 50}))
        self.fit = Fit(self.ch, msgstore_filter=lambda m: isinstance(m, AttrValueChangedOverride))
        self.fit.items.add(self.holder)

    def test_override_set(self):
        # Setup
        holder = self.holder
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr2.id, 77)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        self.assertEqual(self.fit.message_store[-1], AttrValueChangedOverride(self.holder, self.attr2.id))
        self.assertEqual(holder.attributes[self.attr2.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_set_unchanged(self):
        # Setup
        holder = self.holder
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr2.id, 10)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertEqual(holder.attributes[self.attr2.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr2.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr2.id, 88)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        self.assertEqual(self.fit.message_store[-1], AttrValueChangedOverride(self.holder, self.attr2.id))
        self.assertEqual(holder.attributes[self.attr2.id], 88)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 94)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_reset_unchanged(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr2.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_set(self.attr2.id, 77)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertEqual(holder.attributes[self.attr2.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr2.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_del(self.attr2.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        self.assertEqual(self.fit.message_store[-1], AttrValueChangedOverride(self.holder, self.attr2.id))
        self.assertEqual(holder.attributes[self.attr2.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_unchanged(self):
        # Setup
        holder = self.holder
        # Force calculation of attribute by requesting it. Otherwise
        # its modified value will not be calculated and when deleting
        # override, message about changed value will be sent
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        holder.attributes._override_set(self.attr2.id, 10)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_del(self.attr2.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertEqual(holder.attributes[self.attr2.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_delete_persistent(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr2.id, 77, persist=True)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes._override_del(self.attr2.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        self.assertEqual(self.fit.message_store[-1], AttrValueChangedOverride(self.holder, self.attr2.id))
        self.assertEqual(holder.attributes[self.attr2.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_clear(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr2.id, 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        self.assertEqual(self.fit.message_store[-1], AttrValueChangedOverride(self.holder, self.attr2.id))
        self.assertEqual(holder.attributes[self.attr2.id], 10)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 55)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)

    def test_override_clear_persistent(self):
        # Setup
        holder = self.holder
        holder.attributes._override_set(self.attr2.id, 77, persist=True)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        holder.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertEqual(holder.attributes[self.attr2.id], 77)
        self.assertAlmostEqual(holder.attributes[self.attr3.id], 88.5)
        # Cleanup
        self.fit.items.remove(holder)
        self.assert_calculator_buffers_empty(self.fit)
