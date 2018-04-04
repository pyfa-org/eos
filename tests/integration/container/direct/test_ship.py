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


from eos import Fit
from eos import Ship
from eos import Stance
from tests.integration.container.testcase import ContainerTestCase


class TestDirectItemShip(ContainerTestCase):

    def test_none_to_none(self):
        fit = Fit()
        # Action
        fit.ship = None
        # Verification
        self.assertIsNone(fit.ship)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_to_item(self):
        fit = Fit()
        item = Ship(self.mktype().id)
        # Action
        fit.ship = item
        # Verification
        self.assertIs(fit.ship, item)
        # Cleanup
        fit.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_to_item_type_failure(self):
        fit = Fit()
        item = Stance(self.mktype().id)
        # Action
        with self.assertRaises(TypeError):
            fit.ship = item
        # Verification
        self.assertIsNone(fit.ship)
        # Check that item which failed to be added can be assigned to other
        # field
        fit.stance = item
        # Cleanup
        fit.stance = None
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_to_item_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item = Ship(self.mktype().id)
        fit_other.ship = item
        # Action
        with self.assertRaises(ValueError):
            fit.ship = item
        # Verification
        self.assertIsNone(fit.ship)
        self.assertIs(fit_other.ship, item)
        # Cleanup
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_to_item(self):
        fit = Fit()
        ship_type = self.mktype()
        item1 = Ship(ship_type.id)
        item2 = Ship(ship_type.id)
        fit.ship = item1
        # Action
        fit.ship = item2
        # Verification
        self.assertIs(fit.ship, item2)
        # Cleanup
        fit.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_to_item_type_failure(self):
        fit = Fit()
        item1 = Ship(self.mktype().id)
        item2 = Stance(self.mktype().id)
        fit.ship = item1
        # Action
        with self.assertRaises(TypeError):
            fit.ship = item2
        # Verification
        self.assertIs(fit.ship, item1)
        fit.stance = item2
        # Cleanup
        fit.ship = None
        fit.stance = None
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_to_item_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        ship_type = self.mktype()
        item1 = Ship(ship_type.id)
        item2 = Ship(ship_type.id)
        fit.ship = item1
        fit_other.ship = item2
        # Action
        with self.assertRaises(ValueError):
            fit.ship = item2
        # Verification
        self.assertIs(fit.ship, item1)
        self.assertIs(fit_other.ship, item2)
        # Cleanup
        fit.ship = None
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_to_none(self):
        fit = Fit()
        item = Ship(self.mktype().id)
        fit.ship = item
        # Action
        fit.ship = None
        # Verification
        self.assertIsNone(fit.ship)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
