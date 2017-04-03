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


from eos import *
from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestStateSwitching(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(stackable=1)
        src_attr1 = self.ch.attribute()
        src_attr2 = self.ch.attribute()
        src_attr3 = self.ch.attribute()
        src_attr4 = self.ch.attribute()
        src_attr5 = self.ch.attribute()
        modifier_off = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr1.id
        )
        modifier_on = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr2.id
        )
        modifier_act = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr3.id
        )
        modifier_over = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr4.id
        )
        modifier_disabled = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr3.id
        )
        effect_off = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_off])
        effect_on = self.ch.effect(category=EffectCategory.online, modifiers=[modifier_on])
        effect_act = self.ch.effect(category=EffectCategory.active, modifiers=[modifier_act])
        effect_over = self.ch.effect(category=EffectCategory.overload, modifiers=[modifier_over])
        effect_disabled = self.ch.effect(category=EffectCategory.active, modifiers=[modifier_disabled])
        self.item = ModuleHigh(self.ch.type(
            effects=(effect_off, effect_on, effect_act, effect_over, effect_disabled),
            attributes={
                self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3,
                src_attr3.id: 1.5, src_attr4.id: 1.7, src_attr5.id: 2
            }
        ).id)
        self.item._set_effect_activability(effect_disabled.id, False)

    def test_fit_offline(self):
        # Setup
        self.item.state = State.offline
        # Action
        self.fit.modules.high.append(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 110)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_fit_online(self):
        # Setup
        self.item.state = State.online
        # Action
        self.fit.modules.high.append(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_fit_active(self):
        # Setup
        self.item.state = State.active
        # Action
        self.fit.modules.high.append(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 214.5)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_fit_overloaded(self):
        # Setup
        self.item.state = State.overload
        # Action
        self.fit.modules.high.append(self.item)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 364.65)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_switch_up_single(self):
        # Setup
        self.item.state = State.offline
        self.fit.modules.high.append(self.item)
        # Action
        self.item.state = State.online
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_switch_up_multiple(self):
        # Setup
        self.item.state = State.online
        self.fit.modules.high.append(self.item)
        # Action
        self.item.state = State.overload
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 364.65)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_switch_down_single(self):
        # Setup
        self.item.state = State.overload
        self.fit.modules.high.append(self.item)
        # Action
        self.item.state = State.active
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 214.5)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_switch_down_multiple(self):
        # Setup
        self.item.state = State.active
        self.fit.modules.high.append(self.item)
        # Action
        self.item.state = State.offline
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 110)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
