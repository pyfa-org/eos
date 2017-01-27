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


from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import Subsystem, ModuleHigh
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestSubsystemIndex(RestrictionTestCase):
    """Check functionality of subsystem slot index restriction"""

    def test_fail(self):
        # Check that if 2 or more holders are put into single slot
        # index, error is raised
        eve_type = self.ch.type(type_id=1, attributes={Attribute.subsystem_slot: 120})
        holder1 = self.make_item_mock(Subsystem, eve_type)
        holder2 = self.make_item_mock(Subsystem, eve_type)
        self.add_holder(holder1)
        self.add_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.holder_slot_index, 120)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.holder_slot_index, 120)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_other_holder_class(self):
        # Make sure holders of all classes are affected
        eve_type = self.ch.type(type_id=1, attributes={Attribute.subsystem_slot: 120})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_holder(holder1)
        self.add_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.holder_slot_index, 120)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.holder_slot_index, 120)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_attr_eve_type(self):
        # Make sure that eve item attributes are used
        eve_type = self.ch.type(type_id=1, attributes={Attribute.subsystem_slot: 120})
        holder1 = self.make_item_mock(Subsystem, eve_type)
        holder2 = self.make_item_mock(Subsystem, eve_type)
        holder1.attributes = {Attribute.subsystem_slot: 119}
        holder2.attributes = {Attribute.subsystem_slot: 121}
        self.add_holder(holder1)
        self.add_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.holder_slot_index, 120)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.holder_slot_index, 120)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # Single holder which takes some slot shouldn't
        # trigger any errors
        eve_type = self.ch.type(type_id=1, attributes={Attribute.subsystem_slot: 120})
        holder = self.make_item_mock(Subsystem, eve_type)
        self.add_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.subsystem_index)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_different(self):
        # Holders taking different slots shouldn't trigger any errors
        eve_type1 = self.ch.type(type_id=1, attributes={Attribute.subsystem_slot: 120})
        eve_type2 = self.ch.type(type_id=2, attributes={Attribute.subsystem_slot: 121})
        holder1 = self.make_item_mock(Subsystem, eve_type1)
        holder2 = self.make_item_mock(Subsystem, eve_type2)
        self.add_holder(holder1)
        self.add_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.subsystem_index)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.subsystem_index)
        self.assertIsNone(restriction_error2)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
