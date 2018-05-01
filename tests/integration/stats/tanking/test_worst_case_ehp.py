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


from eos import Ship
from eos.const.eve import AttrId
from tests.integration.stats.testcase import StatsTestCase


class TestWorstCaseEhp(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.hp)
        self.mkattr(attr_id=AttrId.em_dmg_resonance)
        self.mkattr(attr_id=AttrId.therm_dmg_resonance)
        self.mkattr(attr_id=AttrId.kin_dmg_resonance)
        self.mkattr(attr_id=AttrId.expl_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_hp)
        self.mkattr(attr_id=AttrId.armor_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_therm_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_kin_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_expl_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_capacity)
        self.mkattr(attr_id=AttrId.shield_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_therm_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_kin_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_expl_dmg_resonance)

    def test_relay(self):
        # Check that stats service relays wcehp stats properly
        self.fit.ship = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.5,
            AttrId.kin_dmg_resonance: 0.5,
            AttrId.expl_dmg_resonance: 0.5,
            AttrId.armor_hp: 15,
            AttrId.armor_em_dmg_resonance: 0.5,
            AttrId.armor_therm_dmg_resonance: 0.8,
            AttrId.armor_kin_dmg_resonance: 0.5,
            AttrId.armor_expl_dmg_resonance: 0.5,
            AttrId.shield_capacity: 20,
            AttrId.shield_em_dmg_resonance: 0.5,
            AttrId.shield_therm_dmg_resonance: 0.5,
            AttrId.shield_kin_dmg_resonance: 0.65,
            AttrId.shield_expl_dmg_resonance: 0.8}).id)
        # Action
        worst_ehp_stats = self.fit.stats.worst_case_ehp
        # Verification
        self.assertAlmostEqual(worst_ehp_stats.hull, 12.5)
        self.assertAlmostEqual(worst_ehp_stats.armor, 18.75)
        self.assertAlmostEqual(worst_ehp_stats.shield, 25)
        self.assertAlmostEqual(worst_ehp_stats.total, 56.25)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_ship_absent(self):
        # Action
        worst_ehp_stats = self.fit.stats.worst_case_ehp
        # Verification
        self.assertAlmostEqual(worst_ehp_stats.hull, 0)
        self.assertAlmostEqual(worst_ehp_stats.armor, 0)
        self.assertAlmostEqual(worst_ehp_stats.shield, 0)
        self.assertAlmostEqual(worst_ehp_stats.total, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        # Action
        worst_ehp_stats = self.fit.stats.worst_case_ehp
        # Verification
        self.assertAlmostEqual(worst_ehp_stats.hull, 0)
        self.assertAlmostEqual(worst_ehp_stats.armor, 0)
        self.assertAlmostEqual(worst_ehp_stats.shield, 0)
        self.assertAlmostEqual(worst_ehp_stats.total, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
