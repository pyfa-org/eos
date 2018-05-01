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


from eos import Drone
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from tests.integration.stats.testcase import StatsTestCase


class TestDroneBandwidth(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.drone_bandwidth)
        self.mkattr(attr_id=AttrId.drone_bandwidth_used)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=AttrId.drone_bandwidth,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 200, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.output, 400)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_output_ship_absent(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.output, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_output_ship_attr_absent(self):
        self.fit.ship = Ship(self.mktype().id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.output, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_output_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.output, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_single_no_rounding(self):
        self.fit.drones.add(Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 55.5555555555}).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(
            self.fit.stats.drone_bandwidth.used, 55.5555555555)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_multiple(self):
        self.fit.drones.add(Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 50}).id,
            state=State.online))
        self.fit.drones.add(Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 30}).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.used, 80)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_state(self):
        self.fit.drones.add(Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 50}).id,
            state=State.online))
        self.fit.drones.add(Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 30}).id,
            state=State.offline))
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.used, 50)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_absent(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.used, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_use_item_not_loaded(self):
        self.fit.drones.add(Drone(
            self.allocate_type_id(),
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.drone_bandwidth.used, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
