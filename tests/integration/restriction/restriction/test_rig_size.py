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


from eos import EffectMode
from eos import Restriction
from eos import Rig
from eos import Ship
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.effect = self.mkeffect(
            effect_id=EffectId.rig_slot,
            category_id=EffectCategoryId.passive)

    def test_fail_size_mismatch(self):
        # Error should be raised when mismatching rig size is added to ship
        self.fit.ship = Ship(self.mktype(attrs={AttrId.rig_size: 6}).id)
        item = Rig(self.mktype(
            attrs={AttrId.rig_size: 10},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.size, 10)
        self.assertEqual(error.allowed_size, 6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_absent(self):
        # When no ship is assigned, no restriction should be applied to ships
        item = Rig(self.mktype(
            attrs={AttrId.rig_size: 10},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_attr_absent(self):
        # If ship doesn't have rig size attribute, no restriction is applied
        # onto rigs
        self.fit.ship = Ship(self.mktype().id)
        item = Rig(self.mktype(
            attrs={AttrId.rig_size: 10},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_not_loaded(self):
        # When no ship is assigned, no restriction should be applied to ships
        self.fit.ship = Ship(self.allocate_type_id())
        item = Rig(self.mktype(
            attrs={AttrId.rig_size: 10},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_effect_disabled(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.rig_size: 6}).id)
        item = Rig(self.mktype(
            attrs={AttrId.rig_size: 10},
            effects=[self.effect]).id)
        item.set_effect_mode(self.effect.id, EffectMode.force_stop)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_effect_absent(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.rig_size: 6}).id)
        item = Rig(self.mktype(attrs={AttrId.rig_size: 10}).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_not_loaded(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.rig_size: 6}).id)
        item = Rig(self.allocate_type_id())
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.rig_size)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
