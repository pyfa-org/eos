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


class TestLauncherSlot(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.launcher_slots_left)
        self.effect = self.ch.effect(
            effect_id=EffectId.launcher_fitted,
            category_id=EffectCategoryId.passive)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr_id=AttributeId.launcher_slots_left,
            operator=ModifierOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.launcher_slots_left: 3, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertEqual(self.fit.stats.launcher_slots.total, 6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_ship(self):
        # None for slot amount when no ship
        # Verification
        self.assertIsNone(self.fit.stats.launcher_slots.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        self.fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.launcher_slots.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_empty(self):
        # Verification
        self.assertEqual(self.fit.stats.launcher_slots.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_multiple(self):
        self.fit.modules.high.append(
            ModuleHigh(self.ch.type(effects=[self.effect]).id))
        self.fit.modules.high.append(
            ModuleHigh(self.ch.type(effects=[self.effect]).id))
        # Verification
        self.assertEqual(self.fit.stats.launcher_slots.used, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_multiple_with_none(self):
        self.fit.modules.high.place(
            1, ModuleHigh(self.ch.type(effects=[self.effect]).id))
        self.fit.modules.high.place(
            3, ModuleHigh(self.ch.type(effects=[self.effect]).id))
        # Verification
        # Positions do not matter
        self.assertEqual(self.fit.stats.launcher_slots.used, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_disabled_effect(self):
        item1 = ModuleHigh(self.ch.type(effects=[self.effect]).id)
        item2 = ModuleHigh(self.ch.type(effects=[self.effect]).id)
        item2.set_effect_mode(self.effect.id, EffectMode.force_stop)
        self.fit.modules.high.append(item1)
        self.fit.modules.high.append(item2)
        # Verification
        self.assertEqual(self.fit.stats.launcher_slots.used, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.launcher_slots_left: 3}).id)
        self.fit.modules.high.append(
            ModuleHigh(self.ch.type(effects=[self.effect]).id))
        self.fit.modules.high.append(
            ModuleHigh(self.ch.type(effects=[self.effect]).id))
        self.fit.source = None
        # Verification
        self.assertEqual(self.fit.stats.launcher_slots.used, 0)
        self.assertIsNone(self.fit.stats.launcher_slots.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
