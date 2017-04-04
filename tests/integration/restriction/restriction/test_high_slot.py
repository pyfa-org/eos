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


class TestHighSlot(RestrictionTestCase):
    """Check functionality of high slot amount restriction"""

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.hi_slots)
        self.effect = self.ch.effect(effect_id=Effect.hi_power, category=EffectCategory.passive)

    def test_fail_excess_single(self):
        # Check that error is raised when number of used
        # slots exceeds slot amount provided by ship
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 0}).id)
        item = ModuleHigh(self.ch.type(effects=[self.effect]).id)
        fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.high_slot)
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
        item = ModuleHigh(self.ch.type(effects=[self.effect]).id)
        fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.high_slot)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_multiple(self):
        # Check that error works for multiple items, and raised
        # only for those which lie out of bounds
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 1}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = ModuleHigh(eve_type.id)
        item2 = ModuleHigh(eve_type.id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.high_slot)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.slots_max_allowed, 1)
        self.assertEqual(restriction_error2.slots_used, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_multiple_with_nones(self):
        # Make sure Nones are processed properly
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 3}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = ModuleHigh(eve_type.id)
        item2 = ModuleHigh(eve_type.id)
        item3 = ModuleHigh(eve_type.id)
        fit.modules.high.place(1, item1)
        fit.modules.high.place(4, item2)
        fit.modules.high.place(6, item3)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.high_slot)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.slots_max_allowed, 3)
        self.assertEqual(restriction_error2.slots_used, 7)
        # Action
        restriction_error3 = self.get_restriction_error(fit, item2, Restriction.high_slot)
        # Verification
        self.assertIsNotNone(restriction_error3)
        self.assertEqual(restriction_error3.slots_max_allowed, 3)
        self.assertEqual(restriction_error3.slots_used, 7)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_equal(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 2}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = ModuleHigh(eve_type.id)
        item2 = ModuleHigh(eve_type.id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_greater(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 5}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = ModuleHigh(eve_type.id)
        item2 = ModuleHigh(eve_type.id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_disabled_effect(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 0}).id)
        item = ModuleHigh(self.ch.type(effects=[self.effect]).id)
        item._set_effect_activability(self.effect.id, False)
        fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_source(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.hi_slots: 0}).id)
        item = ModuleHigh(self.ch.type(effects=[self.effect]).id)
        fit.modules.high.append(item)
        fit.source = None
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.high_slot)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
