# ==============================================================================
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
# ==============================================================================


from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestEffectToggling(CalculatorTestCase):
    """Test effect toggling"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(stackable=1)
        src_attr1 = self.ch.attribute()
        src_attr2 = self.ch.attribute()
        src_attr3 = self.ch.attribute()
        modifier1 = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr1.id
        )
        modifier2 = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr2.id
        )
        modifier_active = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr3.id
        )
        self.effect1 = self.ch.effect(category=EffectCategoryId.passive, modifiers=[modifier1])
        self.effect2 = self.ch.effect(category=EffectCategoryId.passive, modifiers=[modifier2])
        self.effect_active = self.ch.effect(category=EffectCategoryId.active, modifiers=[modifier_active])
        self.item = ModuleHigh(self.ch.type(
            attributes={self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3, src_attr3.id: 2},
            effects=(self.effect1, self.effect2, self.effect_active), default_effect=self.effect_active
        ).id)

    def test_effect_disabling(self):
        # Setup
        self.item.state = State.offline
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_run_mode(self.effect1.id, EffectRunMode.force_stop)
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
        self.item.set_effect_run_mode(self.effect1.id, EffectRunMode.force_stop)
        self.item.set_effect_run_mode(self.effect2.id, EffectRunMode.force_stop)
        self.item.set_effect_run_mode(self.effect_active.id, EffectRunMode.force_stop)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_enabling(self):
        # Setup
        self.item.state = State.offline
        self.item.set_effect_run_mode(self.effect1.id, EffectRunMode.force_stop)
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_run_mode(self.effect1.id, EffectRunMode.state_compliance)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_enabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.item.set_effect_run_mode(self.effect1.id, EffectRunMode.force_stop)
        self.item.set_effect_run_mode(self.effect2.id, EffectRunMode.force_stop)
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_run_mode(self.effect1.id, EffectRunMode.state_compliance)
        self.item.set_effect_run_mode(self.effect2.id, EffectRunMode.state_compliance)
        self.item.set_effect_run_mode(self.effect_active.id, EffectRunMode.state_compliance)
        # Verification
        self.assertAlmostEqual(self.item.attributes[self.tgt_attr.id], 143)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
