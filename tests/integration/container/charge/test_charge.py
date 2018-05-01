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
from eos import Fit
from eos import ModuleHigh
from eos import Stance
from eos import State
from tests.integration.container.testcase import ContainerTestCase


class TestCharge(ContainerTestCase):

    def test_detached_module_none_to_none(self):
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_log_entries(0)

    def test_detached_module_none_to_free_charge(self):
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        # Action
        module.charge = charge
        # Verification
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assertIs(module.charge, charge)

    def test_detached_module_charge_to_free_charge(self):
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge_type = self.mktype()
        charge1 = Charge(charge_type.id)
        charge2 = Charge(charge_type.id)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Verification
        self.assertIs(module.charge, charge2)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge1)
        self.assert_item_buffers_empty(charge2)
        self.assert_log_entries(0)

    def test_detached_module_charge_to_none(self):
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module.charge = charge
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_log_entries(0)

    def test_detached_module_none_to_non_charge(self):
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        non_charge = Stance(self.mktype().id)
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(non_charge)
        self.assert_log_entries(0)

    def test_detached_module_charge_to_non_charge(self):
        fit_other = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        non_charge = Stance(self.mktype().id)
        module.charge = charge
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIs(module.charge, charge)
        fit_other.stance = non_charge
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_item_buffers_empty(non_charge)
        self.assert_solsys_buffers_empty(fit_other.solar_system)
        self.assert_log_entries(0)

    def test_detached_module_none_to_partially_bound_charge(self):
        module_type = self.mktype()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_log_entries(0)

    def test_detached_module_none_to_fully_bound_charge(self):
        fit_other = Fit()
        module_type = self.mktype()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        module_other.charge = charge_other
        fit_other.modules.high.append(module_other)
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_solsys_buffers_empty(fit_other.solar_system)
        self.assert_log_entries(0)

    def test_detached_module_charge_to_partially_bound_charge(self):
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module_other = ModuleHigh(
            self.mktype().id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_log_entries(0)

    def test_detached_module_charge_to_fully_bound_charge(self):
        fit_other = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module_other = ModuleHigh(
            self.mktype().id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        fit_other.modules.high.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_solsys_buffers_empty(fit_other.solar_system)
        self.assert_log_entries(0)

    def test_fit_none_to_none(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        fit.modules.high.append(module)
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_none_to_free_charge(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        fit.modules.high.append(module)
        # Action
        module.charge = charge
        # Verification
        self.assertIs(module.charge, charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_charge_to_free_charge(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge1 = Charge(self.mktype().id)
        charge2 = Charge(self.mktype().id)
        fit.modules.high.append(module)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Verification
        self.assertIs(module.charge, charge2)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge1)
        self.assert_item_buffers_empty(charge2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_charge_to_none(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        fit.modules.high.append(module)
        module.charge = charge
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_none_to_non_charge(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        non_charge = Stance(self.mktype().id)
        fit.modules.high.append(module)
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIsNone(module.charge)
        fit.stance = non_charge
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(non_charge)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_charge_to_non_charge(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        non_charge = Stance(self.mktype().id)
        fit.modules.high.append(module)
        module.charge = charge
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIs(module.charge, charge)
        fit.stance = non_charge
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_item_buffers_empty(non_charge)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_none_to_partially_bound_charge(self):
        fit = Fit()
        module_type = self.mktype()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        module_other.charge = charge_other
        fit.modules.high.append(module)
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_none_to_fully_bound_charge(self):
        fit = Fit()
        fit_other = Fit()
        module_type = self.mktype()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        module_other.charge = charge_other
        fit.modules.high.append(module)
        fit_other.modules.high.append(module_other)
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_solsys_buffers_empty(fit_other.solar_system)
        self.assert_log_entries(0)

    def test_fit_charge_to_partially_bound_charge(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module_other = ModuleHigh(
            self.mktype().id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        fit.modules.high.append(module)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_charge_to_fully_bound_charge(self):
        fit = Fit()
        fit_other = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module_other = ModuleHigh(
            self.mktype().id, state=State.active, charge=None)
        charge_other = Charge(self.mktype().id)
        fit.modules.high.append(module)
        fit_other.modules.high.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_item_buffers_empty(module_other)
        self.assert_item_buffers_empty(charge_other)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_solsys_buffers_empty(fit_other.solar_system)
        self.assert_log_entries(0)

    def test_fit_add_charged_module(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module.charge = charge
        # Action
        fit.modules.high.append(module)
        # Verification
        self.assertEqual(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], module)
        self.assertIs(module.charge, charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_fit_remove_charged_module(self):
        fit = Fit()
        module = ModuleHigh(self.mktype().id, state=State.active, charge=None)
        charge = Charge(self.mktype().id)
        module.charge = charge
        fit.modules.high.append(module)
        # Action
        fit.modules.high.remove(module)
        # Verification
        self.assertEqual(len(fit.modules.high), 0)
        self.assertIs(module.charge, charge)
        # Cleanup
        self.assert_item_buffers_empty(module)
        self.assert_item_buffers_empty(charge)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
