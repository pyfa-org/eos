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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.stats.stat_testcase import StatTestCase


class TestLowSlot(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=AttributeId.low_slots)
        self.effect = self.ch.effect(effect_id=EffectId.lo_power, category=EffectCategoryId.passive)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=AttributeId.low_slots,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        mod_effect = self.ch.effect(category=EffectCategoryId.passive, modifiers=[modifier])
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={AttributeId.low_slots: 3, src_attr.id: 2}, effects=[mod_effect]).id)
        # Verification
        self.assertEqual(fit.stats.low_slots.total, 6)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_ship(self):
        # None for slot amount when no ship
        fit = Fit()
        # Verification
        self.assertIsNone(fit.stats.low_slots.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        fit = Fit()
        fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(fit.stats.low_slots.total)
        # Cleanup
        # Log entry is due to inability to calculate requested attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_use_empty(self):
        fit = Fit()
        # Verification
        self.assertEqual(fit.stats.low_slots.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_multiple(self):
        fit = Fit()
        fit.modules.low.append(ModuleLow(self.ch.type(effects=[self.effect]).id))
        fit.modules.low.append(ModuleLow(self.ch.type(effects=[self.effect]).id))
        # Verification
        self.assertEqual(fit.stats.low_slots.used, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_multiple_with_none(self):
        fit = Fit()
        fit.modules.low.place(1, ModuleLow(self.ch.type(effects=[self.effect]).id))
        fit.modules.low.place(3, ModuleLow(self.ch.type(effects=[self.effect]).id))
        # Verification
        self.assertEqual(fit.stats.low_slots.used, 4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_disabled_effect(self):
        fit = Fit()
        item1 = ModuleLow(self.ch.type(effects=[self.effect]).id)
        item2 = ModuleLow(self.ch.type(effects=[self.effect]).id)
        item2.set_effect_run_mode(self.effect.id, EffectRunMode.force_stop)
        fit.modules.low.append(item1)
        fit.modules.low.append(item2)
        # Verification
        self.assertEqual(fit.stats.low_slots.used, 1)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_other_item_class(self):
        fit = Fit()
        fit.modules.high.place(3, ModuleHigh(self.ch.type(effects=[self.effect]).id))
        # Verification
        self.assertEqual(fit.stats.low_slots.used, 4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={AttributeId.low_slots: 3}).id)
        fit.modules.low.append(ModuleLow(self.ch.type(effects=[self.effect]).id))
        fit.modules.low.append(ModuleLow(self.ch.type(effects=[self.effect]).id))
        fit.source = None
        # Verification
        self.assertEqual(fit.stats.low_slots.used, 0)
        self.assertIsNone(fit.stats.low_slots.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
