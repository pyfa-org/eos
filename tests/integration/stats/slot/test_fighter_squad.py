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


from eos import Drone
from eos import FighterSquad
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from tests.integration.stats.testcase import StatsTestCase


class TestFighterSquad(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.fighter_tubes)

    def test_output(self):
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=AttrId.fighter_tubes,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.fighter_tubes: 3, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertEqual(self.fit.stats.fighter_squads.total, 6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_ship(self):
        # None for slot quantity when no ship
        self.fit.ship = None
        # Verification
        self.assertIsNone(self.fit.stats.fighter_squads.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_attr(self):
        # None for slot quantity when no attribute on ship
        self.fit.ship = Ship(self.mktype().id)
        # Verification
        self.assertIsNone(self.fit.stats.fighter_squads.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_empty(self):
        # Verification
        self.assertEqual(self.fit.stats.fighter_squads.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_multiple(self):
        self.fit.fighters.add(FighterSquad(self.mktype().id))
        self.fit.fighters.add(FighterSquad(self.mktype().id))
        # Verification
        self.assertEqual(self.fit.stats.fighter_squads.used, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_other_item_class(self):
        self.fit.drones.add(Drone(self.mktype().id))
        # Verification
        self.assertEqual(self.fit.stats.fighter_squads.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.fighter_tubes: 3}).id)
        self.fit.fighters.add(FighterSquad(self.mktype().id))
        self.fit.fighters.add(FighterSquad(self.mktype().id))
        self.fit.source = None
        # Verification
        self.assertEqual(self.fit.stats.fighter_squads.used, 0)
        self.assertIsNone(self.fit.stats.fighter_squads.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
