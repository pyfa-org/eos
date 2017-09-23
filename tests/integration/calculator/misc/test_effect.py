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
from eos.data.cachable.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


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
        self.effect1 = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier1])
        self.effect2 = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier2])
        self.effect_active = self.ch.effect(category=EffectCategory.active, modifiers=[modifier_active])
        self.item = ModuleHigh(self.ch.type(
            effects=(self.effect1, self.effect2, self.effect_active),
            attributes={self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3, src_attr3.id: 2}
        ).id)

    def test_effect_disabling(self):
        # Setup
        self.item.state = State.offline
        self.fit.modules.high.append(self.item)
        # Action
        self.item._set_effect_activability(self.effect1.id, False)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 130)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_disabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.fit.modules.high.append(self.item)
        # Action
        self.item._set_effect_activability(self.effect1.id, False)
        self.item._set_effect_activability(self.effect2.id, False)
        self.item._set_effect_activability(self.effect_active.id, False)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_enabling(self):
        # Setup
        self.item.state = State.offline
        self.item._set_effect_activability(self.effect1.id, False)
        self.fit.modules.high.append(self.item)
        # Action
        self.item._set_effect_activability(self.effect1.id, True)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_enabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.item._set_effect_activability(self.effect1.id, False)
        self.item._set_effect_activability(self.effect2.id, False)
        self.fit.modules.high.append(self.item)
        # Action
        self.item._set_effect_activability(self.effect1.id, True)
        self.item._set_effect_activability(self.effect2.id, True)
        self.item._set_effect_activability(self.effect_active.id, True)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
