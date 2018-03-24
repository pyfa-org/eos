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


from eos import Character
from eos import Drone
from eos import ModuleHigh
from eos import Restriction
from eos import State
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestLaunchedDrone(RestrictionTestCase):
    """Check functionality of max launched drone restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.max_active_drones)

    def test_fail_single(self):
        # Check that error is raised when quantity of used slots exceeds slot
        # quantity provided by char
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 0}).id)
        item = Drone(self.mktype().id, state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple(self):
        # Check that error works for multiple items
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 1}).id)
        item_type = self.mktype()
        item1 = Drone(item_type.id, state=State.online)
        item2 = Drone(item_type.id, state=State.online)
        self.fit.drones.add(item1)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.launched_drone)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.used, 2)
        self.assertEqual(error1.total, 1)
        # Action
        error2 = self.get_error(item2, Restriction.launched_drone)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.used, 2)
        self.assertEqual(error2.total, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_char_absent(self):
        # When stats module does not specify total slot quantity, make sure it's
        # assumed to be 0
        self.fit.character = None
        item = Drone(self.mktype().id, state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_char_attr_absent(self):
        self.fit.character = Character(self.mktype().id)
        item = Drone(self.mktype().id, state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_char_not_loaded(self):
        self.fit.character = Character(self.allocate_type_id())
        item = Drone(self.mktype().id, state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 2}).id)
        item_type = self.mktype()
        item1 = Drone(item_type.id, state=State.online)
        item2 = Drone(item_type.id, state=State.online)
        self.fit.drones.add(item1)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_greater(self):
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 5}).id)
        item_type = self.mktype()
        item1 = Drone(item_type.id, state=State.online)
        item2 = Drone(item_type.id, state=State.online)
        self.fit.drones.add(item1)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_state(self):
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 0}).id)
        item = Drone(self.mktype().id, state=State.offline)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_not_loaded(self):
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 0}).id)
        item = Drone(self.allocate_type_id(), state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_other_class(self):
        self.fit.character = Character(self.mktype(
            attrs={AttrId.max_active_drones: 0}).id)
        item = ModuleHigh(self.mktype().id, state=State.online)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.launched_drone)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
