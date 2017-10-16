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
from tests.integration.sim.rah.rah_testcase import RahSimTestCase


class TestRahSimSource(RahSimTestCase):

    def test_no_source(self):
        # Setup
        ship_item = Ship(self.make_ship_eve_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship_item
        rah_item = ModuleLow(
            self.make_rah_eve_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah_item)
        self.fit.source = None
        # Verification
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_em.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_therm.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_kin.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_exp.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_em.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_therm.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_kin.id]
        with self.assertRaises(KeyError):
            rah_item.attributes[self.armor_exp.id]
        # Cleanup
        self.assertEqual(len(self.log), 8)
        self.assert_fit_buffers_empty(self.fit)
