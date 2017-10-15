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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction."""

    def setUp(self):
        super().setUp()
        self.effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category=EffectCategoryId.passive)

    def test_fail_mismatch(self):
        # Error should be raised when mismatching rig size is added to ship
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_size: 6}).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.rig_size: 10}, effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_size)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.item_size, 10)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_no_ship(self):
        # When no ship is assigned, no restriction should be applied to ships
        item = Rig(self.ch.type(
            attributes={AttributeId.rig_size: 10}, effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_size)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_ship_no_attr(self):
        # If ship doesn't have rig size attribute, no restriction is applied
        # onto rigs
        self.fit.ship = Ship(self.ch.type().id)
        item = Rig(self.ch.type(
            attributes={AttributeId.rig_size: 10}, effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_size)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_disabled_effect(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_size: 6}).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.rig_size: 10}, effects=[self.effect]).id)
        item.set_effect_run_mode(self.effect.id, EffectRunMode.force_stop)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_size)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_size: 6}).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.rig_size: 10}, effects=[self.effect]).id)
        self.fit.rigs.add(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_size)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
