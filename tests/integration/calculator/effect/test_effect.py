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
from eos.fit.message import EffectsEnabled, EffectsDisabled
from tests.integration.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestEffectToggling(CalculatorTestCase):
    """Test effect toggling"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(stackable=1)
        src_attr1 = self.ch.attribute()
        src_attr2 = self.ch.attribute()
        src_attr3 = self.ch.attribute()
        modifier1 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr1.id
        )
        modifier2 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr2.id
        )
        modifier_active = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr3.id
        )
        self.effect1 = self.ch.effect(category=EffectCategory.passive)
        self.effect1.modifiers = (modifier1,)
        self.effect2 = self.ch.effect(category=EffectCategory.passive)
        self.effect2.modifiers = (modifier2,)
        self.effect_active = self.ch.effect(category=EffectCategory.active)
        self.effect_active.modifiers = (modifier_active,)
        self.item = IndependentItem(self.ch.type(
            effects=(self.effect1, self.effect2, self.effect_active),
            attributes={self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3, src_attr3.id: 2}
        ))

    def test_effect_disabling(self):
        # Setup
        self.item.state = State.offline
        self.fit.items.add(self.item)
        # Action
        self.item._blocked_effect_ids.add(self.effect1.id)
        self.fit._calculator._notify(EffectsDisabled(self.item, (self.effect1.id,)))
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 130)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_disabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.fit.items.add(self.item)
        # Action
        self.item._blocked_effect_ids.update((self.effect1.id, self.effect2.id, self.effect_active.id))
        self.fit._calculator._notify(EffectsDisabled(
            self.item, (self.effect1.id, self.effect2.id, self.effect_active.id)
        ))
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_enabling(self):
        # Setup
        self.item.state = State.offline
        self.item._blocked_effect_ids.add(self.effect1.id)
        self.fit.items.add(self.item)
        # Action
        self.fit._calculator._notify(EffectsEnabled(self.item, (self.effect1.id,)))
        self.item._blocked_effect_ids.discard(self.effect1.id)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_enabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.item._blocked_effect_ids.update((self.effect1.id, self.effect2.id))
        self.fit.items.add(self.item)
        # Action
        self.fit._calculator._notify(EffectsEnabled(
            self.item, (self.effect1.id, self.effect2.id, self.effect_active.id)
        ))
        self.item._blocked_effect_ids.difference_update((self.effect1.id, self.effect2.id, self.effect_active.id))
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
