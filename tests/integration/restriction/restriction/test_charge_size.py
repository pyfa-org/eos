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


from eos import Charge
from eos import ModuleHigh
from eos import Restriction
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestChargeSize(RestrictionTestCase):
    """Check functionality of charge size restriction."""

    def test_fail_lesser(self):
        charge = Charge(self.mktype(attrs={AttrId.charge_size: 2}).id)
        container = ModuleHigh(
            self.mktype(attrs={AttrId.charge_size: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.size, 2)
        self.assertEqual(error2.allowed_size, 3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_greater(self):
        charge = Charge(self.mktype(attrs={AttrId.charge_size: 2}).id)
        container = ModuleHigh(
            self.mktype(attrs={AttrId.charge_size: 1}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.size, 2)
        self.assertEqual(error2.allowed_size, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_charge_no_attr(self):
        charge = Charge(self.mktype().id)
        container = ModuleHigh(
            self.mktype(attrs={AttrId.charge_size: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.size, None)
        self.assertEqual(error2.allowed_size, 3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        charge = Charge(self.mktype(attrs={AttrId.charge_size: 2}).id)
        container = ModuleHigh(
            self.mktype(attrs={AttrId.charge_size: 2}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.charge_size)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_container_attr(self):
        charge = Charge(self.mktype(attrs={AttrId.charge_size: 2}).id)
        container = ModuleHigh(self.mktype().id, state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.charge_size)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_autocharge(self):
        # Make sure autocharge size is ignored
        autocharge_type = self.mktype(attrs={AttrId.charge_size: 2})
        container_effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.target,
            customize=True)
        container = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.charge_size: 3,
                    AttrId.ammo_loaded: autocharge_type.id},
                effects=[container_effect]).id,
            state=State.offline)
        self.fit.modules.high.append(container)
        self.assertIn(container_effect.id, container.autocharges)
        autocharge = container.autocharges[container_effect.id]
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(autocharge, Restriction.charge_size)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        charge = Charge(self.mktype(attrs={AttrId.charge_size: 2}).id)
        container = ModuleHigh(
            self.mktype(attrs={AttrId.charge_size: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        self.fit.source = None
        # Action
        error1 = self.get_error(container, Restriction.charge_size)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.charge_size)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
