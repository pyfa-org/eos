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


from eos import Charge
from eos import Fit
from eos import ModuleHigh
from eos import ResistProfile
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgCommonDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.reload_time)
        self.mkattr(attr_id=AttrId.dmg_mult)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.mkattr(attr_id=AttrId.module_reactivation_delay)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)

    def test_effective(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_mult: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.therm_dmg: 6.3,
            AttrId.kin_dmg: 7.4,
            AttrId.expl_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        dps = item.get_dps(tgt_resists=profile)
        self.assertAlmostEqual(dps.em, 20.8)
        self.assertAlmostEqual(dps.thermal, 25.2)
        self.assertAlmostEqual(dps.kinetic, 7.4)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 53.4)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_reactivation_shorter_than_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_mult: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 6500,
                    AttrId.module_reactivation_delay: 1500},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.therm_dmg: 6.3,
            AttrId.kin_dmg: 7.4,
            AttrId.expl_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_dps(reload=True)
        self.assertAlmostEqual(dps.em, 5.2)
        self.assertAlmostEqual(dps.thermal, 6.3)
        self.assertAlmostEqual(dps.kinetic, 7.4)
        self.assertAlmostEqual(dps.explosive, 8.5)
        self.assertAlmostEqual(dps.total, 27.4)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_reactivation_longer_than_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_mult: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 6500,
                    AttrId.module_reactivation_delay: 19500},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.therm_dmg: 6.3,
            AttrId.kin_dmg: 7.4,
            AttrId.expl_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_dps(reload=True)
        self.assertAlmostEqual(dps.em, 0.65)
        self.assertAlmostEqual(dps.thermal, 0.7875)
        self.assertAlmostEqual(dps.kinetic, 0.925)
        self.assertAlmostEqual(dps.explosive, 1.0625)
        self.assertAlmostEqual(dps.total, 3.425)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_not_loaded(self):
        fit = Fit()
        item = ModuleHigh(self.allocate_type_id(), state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_dps()
        self.assertAlmostEqual(dps.em, 0)
        self.assertAlmostEqual(dps.thermal, 0)
        self.assertAlmostEqual(dps.kinetic, 0)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
