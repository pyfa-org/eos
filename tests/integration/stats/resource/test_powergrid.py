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
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModAffecteeFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.stats.testcase import StatsTestCase


class TestPowergrid(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.power_output)
        self.mkattr(attr_id=AttrId.power)
        self.effect = self.mkeffect(
            effect_id=EffectId.online,
            category_id=EffectCategoryId.online)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=AttrId.power_output,
            operator=ModOperator.post_mul,
            affector_attr_id=src_attr.id)
        mod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.power_output: 200, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.output, 400)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_output_ship_absent(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.output, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_output_ship_attr_absent(self):
        self.fit.ship = Ship(self.mktype().id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.output, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_output_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.output, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_single(self):
        # Check that modified consumption attribute is used
        src_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=AttrId.power,
            operator=ModOperator.post_mul,
            affector_attr_id=src_attr.id)
        mod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.fit.modules.high.append(ModuleHigh(
            self.mktype(
                attrs={AttrId.power: 100, src_attr.id: 0.5},
                effects=(self.effect, mod_effect)).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_multiple(self):
        self.fit.modules.high.append(ModuleHigh(
            self.mktype(attrs={AttrId.power: 50}, effects=[self.effect]).id,
            state=State.online))
        self.fit.modules.high.append(ModuleHigh(
            self.mktype(attrs={AttrId.power: 30}, effects=[self.effect]).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 80)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_rounding(self):
        self.fit.modules.high.append(ModuleHigh(
            self.mktype(
                attrs={AttrId.power: 55.5555555555},
                effects=[self.effect]).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 55.56)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_state(self):
        self.fit.modules.high.append(ModuleHigh(
            self.mktype(attrs={AttrId.power: 50}, effects=[self.effect]).id,
            state=State.online))
        self.fit.modules.high.append(ModuleHigh(
            self.mktype(attrs={AttrId.power: 30}, effects=[self.effect]).id,
            state=State.offline))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_effect_absent(self):
        item1 = ModuleHigh(
            self.mktype(attrs={AttrId.power: 50}, effects=[self.effect]).id,
            state=State.online)
        item2 = ModuleHigh(
            self.mktype(attrs={AttrId.power: 30}).id,
            state=State.online)
        self.fit.modules.high.append(item1)
        self.fit.modules.high.append(item2)
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_effect_disabled(self):
        item1 = ModuleHigh(
            self.mktype(attrs={AttrId.power: 50}, effects=[self.effect]).id,
            state=State.online)
        item2 = ModuleHigh(
            self.mktype(attrs={AttrId.power: 30}, effects=[self.effect]).id,
            state=State.online)
        item2.set_effect_mode(self.effect.id, EffectMode.force_stop)
        self.fit.modules.high.append(item1)
        self.fit.modules.high.append(item2)
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_absent(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_not_loaded(self):
        self.fit.modules.high.append(ModuleHigh(
            self.allocate_type_id(),
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
