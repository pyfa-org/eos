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


from eos import Charge
from eos import ModuleHigh
from eos import Restriction
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestState(RestrictionTestCase):
    """Check functionality of item state restriction."""

    def test_fail_item_state_higher(self):
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(
            self.mktype(effects=[effect], default_effect=effect).id,
            state=State.overload)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.state)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.state, State.overload)
        self.assertCountEqual(
            error.allowed_states,
            (State.offline, State.online, State.active))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_item_state_higher_effects_absent(self):
        item = ModuleHigh(self.mktype().id, state=State.overload)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.state)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.state, State.overload)
        self.assertCountEqual(error.allowed_states, [State.offline])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_state_lower(self):
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(
            self.mktype(effects=[effect], default_effect=effect).id,
            state=State.online)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.state)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_state_equal(self):
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(
            self.mktype(effects=[effect], default_effect=effect).id,
            state=State.active)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.state)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_exception_charge(self):
        # Charges do not store state at all (inherit from parent), thus they
        # should not be checked
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(
            self.mktype(effects=[effect], default_effect=effect).id,
            state=State.active)
        charge = Charge(self.mktype().id)
        item.charge = charge
        self.fit.modules.high.append(item)
        # Action
        error1 = self.get_error(item, Restriction.state)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(charge, Restriction.state)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_exception_autocharge(self):
        # Autocharges are the same as charges, inherit state from container
        autocharge_type = self.mktype()
        container_effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.target)
        container = ModuleHigh(
            self.mktype(
                attrs={AttrId.ammo_loaded: autocharge_type.id},
                effects=[container_effect]).id,
            state=State.active)
        self.fit.modules.high.append(container)
        self.assertIn(container_effect.id, container.autocharges)
        autocharge = container.autocharges[container_effect.id]
        # Action
        error = self.get_error(autocharge, Restriction.state)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_not_loaded(self):
        item = ModuleHigh(self.allocate_type_id(), state=State.overload)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.state)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
