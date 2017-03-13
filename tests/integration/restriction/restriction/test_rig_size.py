# ===============================================================================
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
# ===============================================================================


from eos import *
from eos.const.eos import Restriction
from eos.const.eve import Attribute
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction"""

    def test_fail_mismatch(self):
        # Error should be raised when mismatching rig size
        # is added to ship
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.rig_size: 10})
        item = Rig(eve_type.id)
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.rig_size: 6})
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        restriction_error = self.get_restriction_error(fit, item, Restriction.rig_size)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.item_size, 10)
        self.remove_item(item)
        fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_attr_eve_type(self):
        # Eve type value must be taken
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.rig_size: 10})
        item = Rig(eve_type.id)
        item.attributes = {Attribute.rig_size: 5}
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.rig_size: 6})
        ship_item = Ship(ship_eve_type.id)
        ship_item.attributes = {Attribute.rig_size: 5}
        fit.ship = ship_item
        restriction_error = self.get_restriction_error(fit, item, Restriction.rig_size)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.item_size, 10)
        self.remove_item(item)
        fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_ship(self):
        # When no ship is assigned, no restriction
        # should be applied to ships
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.rig_size: 10})
        item = Rig(eve_type.id)
        self.add_item(item)
        restriction_error = self.get_restriction_error(fit, item, Restriction.rig_size)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_ship_no_attr(self):
        # If ship doesn't have rig size attribute,
        # no restriction is applied onto rigs
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.rig_size: 10})
        item = Rig(eve_type.id)
        self.add_item(item)
        ship_eve_type = self.ch.type()
        ship_item = Ship(ship_eve_type.id)
        ship_item.attributes = {}
        fit.ship = ship_item
        restriction_error = self.get_restriction_error(fit, item, Restriction.rig_size)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
