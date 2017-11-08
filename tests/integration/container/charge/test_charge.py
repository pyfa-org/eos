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
from tests.integration.container.container_testcase import ContainerTestCase


class TestCharge(ContainerTestCase):

    def assert_fit_buffers_empty(self, fit, clear_all=True):
        # Here we're not testing on-fit containers thus can safely clear them
        ContainerTestCase.assert_fit_buffers_empty(
            self, fit, clear_all=clear_all)

    def test_detached_module_none_to_none(self):
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_none_to_free_charge(self):
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        # Action
        module.charge = charge
        # Verification
        self.assertIs(module.charge, charge)

    def test_detached_module_charge_to_free_charge(self):
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge_type = self.ch.type()
        charge1 = Charge(charge_type.id)
        charge2 = Charge(charge_type.id)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Verification
        self.assertIs(module.charge, charge2)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_charge_to_none(self):
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module.charge = charge
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_none_to_non_charge(self):
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        non_charge = Stance(self.ch.type().id)
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_charge_to_non_charge(self):
        fit_other = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        non_charge = Stance(self.ch.type().id)
        module.charge = charge
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIs(module.charge, charge)
        fit_other.stance = non_charge
        # Cleanup
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_none_to_partially_bound_charge(self):
        module_type = self.ch.type()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_none_to_fully_bound_charge(self):
        fit_other = Fit()
        module_type = self.ch.type()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
        module_other.charge = charge_other
        fit_other.modules.high.append(module_other)
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_charge_to_partially_bound_charge(self):
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module_other = ModuleHigh(
            self.ch.type().id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_detached_module_charge_to_fully_bound_charge(self):
        fit_other = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module_other = ModuleHigh(
            self.ch.type().id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
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
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_none_to_none(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        fit.modules.high.append(module)
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_none_to_free_charge(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        fit.modules.high.append(module)
        # Action
        module.charge = charge
        # Verification
        self.assertIs(module.charge, charge)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_charge_to_free_charge(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge1 = Charge(self.ch.type().id)
        charge2 = Charge(self.ch.type().id)
        fit.modules.high.append(module)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Verification
        self.assertIs(module.charge, charge2)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_charge_to_none(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        fit.modules.high.append(module)
        module.charge = charge
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_none_to_non_charge(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        non_charge = Stance(self.ch.type().id)
        fit.modules.high.append(module)
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIsNone(module.charge)
        fit.stance = non_charge
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_charge_to_non_charge(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        non_charge = Stance(self.ch.type().id)
        fit.modules.high.append(module)
        module.charge = charge
        # Action
        with self.assertRaises(TypeError):
            module.charge = non_charge
        # Verification
        self.assertIs(module.charge, charge)
        fit.stance = non_charge
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_none_to_partially_bound_charge(self):
        fit = Fit()
        module_type = self.ch.type()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
        module_other.charge = charge_other
        fit.modules.high.append(module)
        # Action
        with self.assertRaises(ValueError):
            module.charge = charge_other
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_none_to_fully_bound_charge(self):
        fit = Fit()
        fit_other = Fit()
        module_type = self.ch.type()
        module = ModuleHigh(module_type.id, state=State.active, charge=None)
        module_other = ModuleHigh(
            module_type.id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
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
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_charge_to_partially_bound_charge(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module_other = ModuleHigh(
            self.ch.type().id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
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
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_charge_to_fully_bound_charge(self):
        fit = Fit()
        fit_other = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module_other = ModuleHigh(
            self.ch.type().id, state=State.active, charge=None)
        charge_other = Charge(self.ch.type().id)
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
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_add_charged_module(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module.charge = charge
        # Action
        fit.modules.high.append(module)
        # Verification
        self.assertEqual(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], module)
        self.assertIs(module.charge, charge)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fit_remove_charged_module(self):
        fit = Fit()
        module = ModuleHigh(self.ch.type().id, state=State.active, charge=None)
        charge = Charge(self.ch.type().id)
        module.charge = charge
        fit.modules.high.append(module)
        # Action
        fit.modules.high.remove(module)
        # Verification
        self.assertEqual(len(fit.modules.high), 0)
        self.assertIs(module.charge, charge)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
