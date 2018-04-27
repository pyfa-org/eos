# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from eos import EffectMode
from eos import ModuleHigh
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestEffectToggling(CalculatorTestCase):
    """Test effect toggling."""

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr(stackable=1)
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        src_attr3 = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr1.id)
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr2.id)
        modifier_active = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr3.id)
        self.effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier1])
        self.effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier2])
        self.effect_active = self.mkeffect(
            category_id=EffectCategoryId.active, modifiers=[modifier_active])
        self.item = ModuleHigh(self.mktype(
            attrs={
                self.tgt_attr.id: 100, src_attr1.id: 1.1,
                src_attr2.id: 1.3, src_attr3.id: 2},
            effects=(self.effect1, self.effect2, self.effect_active),
            default_effect=self.effect_active).id)

    def test_effect_disabling(self):
        # Setup
        self.item.state = State.offline
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_mode(self.effect1.id, EffectMode.force_stop)
        # Verification
        self.assertAlmostEqual(self.item.attrs[self.tgt_attr.id], 130)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_disabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_mode(self.effect1.id, EffectMode.force_stop)
        self.item.set_effect_mode(self.effect2.id, EffectMode.force_stop)
        self.item.set_effect_mode(self.effect_active.id, EffectMode.force_stop)
        # Verification
        self.assertAlmostEqual(self.item.attrs[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_enabling(self):
        # Setup
        self.item.state = State.offline
        self.item.set_effect_mode(self.effect1.id, EffectMode.force_stop)
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_mode(self.effect1.id, EffectMode.state_compliance)
        # Verification
        self.assertAlmostEqual(self.item.attrs[self.tgt_attr.id], 143)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_enabling_multiple(self):
        # Setup
        self.item.state = State.offline
        self.item.set_effect_mode(self.effect1.id, EffectMode.force_stop)
        self.item.set_effect_mode(self.effect2.id, EffectMode.force_stop)
        self.fit.modules.high.append(self.item)
        # Action
        self.item.set_effect_mode(self.effect1.id, EffectMode.state_compliance)
        self.item.set_effect_mode(self.effect2.id, EffectMode.state_compliance)
        self.item.set_effect_mode(
            self.effect_active.id, EffectMode.state_compliance)
        # Verification
        self.assertAlmostEqual(self.item.attrs[self.tgt_attr.id], 143)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
