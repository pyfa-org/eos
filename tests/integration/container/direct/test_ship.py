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
from tests.integration.container.container_testcase import ContainerTestCase


class TestDirectItemShip(ContainerTestCase):

    def test_none_to_none(self):
        fit = Fit()
        # Action
        fit.ship = None
        # Verification
        self.assertIsNone(fit.ship)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_none_to_item(self):
        fit = Fit()
        item = Ship(self.ch.type().id)
        # Action
        fit.ship = item
        # Verification
        self.assertIs(fit.ship, item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_none_to_item_type_failure(self):
        fit = Fit()
        item = Stance(self.ch.type().id)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'ship', item)
        # Verification
        self.assertIsNone(fit.ship)
        # Check that item which failed to be added
        # can be assigned to other field
        fit.stance = item
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_none_to_item_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item = Ship(self.ch.type().id)
        fit_other.ship = item
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'ship', item)
        # Verification
        self.assertIsNone(fit.ship)
        self.assertIs(fit_other.ship, item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_item_to_item(self):
        fit = Fit()
        ship_eve_type = self.ch.type()
        item1 = Ship(ship_eve_type.id)
        item2 = Ship(ship_eve_type.id)
        fit.ship = item1
        # Action
        fit.ship = item2
        # Verification
        self.assertIs(fit.ship, item2)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_to_item_type_failure(self):
        fit = Fit()
        item1 = Ship(self.ch.type().id)
        item2 = Stance(self.ch.type().id)
        fit.ship = item1
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'ship', item2)
        # Verification
        self.assertIs(fit.ship, item1)
        fit.stance = item2
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_to_item_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        ship_eve_type = self.ch.type()
        item1 = Ship(ship_eve_type.id)
        item2 = Ship(ship_eve_type.id)
        fit.ship = item1
        fit_other.ship = item2
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'ship', item2)
        # Verification
        self.assertIs(fit.ship, item1)
        self.assertIs(fit_other.ship, item2)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_item_to_none(self):
        fit = Fit()
        item = Ship(self.ch.type().id)
        fit.ship = item
        # Action
        fit.ship = None
        # Verification
        self.assertIsNone(fit.ship)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
