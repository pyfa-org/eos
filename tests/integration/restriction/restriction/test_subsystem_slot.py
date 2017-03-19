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
from eos.const.eve import Attribute, Effect, EffectCategory
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestSubsystemSlot(RestrictionTestCase):
    """Check functionality of subsystem slot amount restriction"""

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.max_subsystems)
        self.slot_effect = self.ch.effect(effect_id=Effect.subsystem, category=EffectCategory.passive)

    def test_fail_excess_single(self):
        # Check that error is raised when number of used
        # slots exceeds slot amount provided by ship
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.max_subsystems: 0}).id)
        item = Subsystem(self.ch.type(effects=(self.slot_effect,)).id)
        fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_single_no_ship(self):
        # When stats module does not specify total slot amount,
        # make sure it's assumed to be 0
        fit = Fit()
        item = Subsystem(self.ch.type(effects=(self.slot_effect,)).id)
        fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_multiple(self):
        # Check that error works for multiple items
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.max_subsystems: 1}).id)
        eve_type = self.ch.type(effects=(self.slot_effect,))
        item1 = Subsystem(eve_type.id)
        item2 = Subsystem(eve_type.id)
        fit.subsystems.add(item1)
        fit.subsystems.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.slots_max_allowed, 1)
        self.assertEqual(restriction_error1.slots_used, 2)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.slots_max_allowed, 1)
        self.assertEqual(restriction_error2.slots_used, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_equal(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.max_subsystems: 2}).id)
        eve_type = self.ch.type(effects=(self.slot_effect,))
        item1 = Subsystem(eve_type.id)
        item2 = Subsystem(eve_type.id)
        fit.subsystems.add(item1)
        fit.subsystems.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_greater(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.max_subsystems: 5}).id)
        eve_type = self.ch.type(effects=(self.slot_effect,))
        item1 = Subsystem(eve_type.id)
        item2 = Subsystem(eve_type.id)
        fit.subsystems.add(item1)
        fit.subsystems.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_other_item_class(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.max_subsystems: 0}).id)
        item = ModuleLow(self.ch.type(effects=(self.slot_effect,)).id)
        fit.modules.low.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
