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


from unittest.mock import Mock

from eos.const.eos import State
from eos.fit.container import ItemList
from eos.fit.item import ModuleHigh, Charge
from eos.fit.messages import ItemAdded, ItemRemoved
from tests.container.environment import Fit, OtherItem
from tests.container.container_testcase import ContainerTestCase


class ChargeableAssertion:

    def __init__(self, test, loaded):
        self.test = test
        self.loaded = loaded

    def __enter__(self):
        self.test.charged_flag = self.loaded

    def __exit__(self, *args):
        del self.test.charged_flag


class TestModuleCharge(ContainerTestCase):
    """
    Everything related to charge switching is tested here.
    """

    def chargeable_assertions(self, charged):
        return ChargeableAssertion(self, charged)

    def make_fit(self):

        def charge_relationship_assertion(fit, message):
            item = message.item
            # If link variable is True, we make sure
            # there's link between module and charge upon
            # addition to services. If False, we ensure
            # there's no link.
            charged = getattr(self, 'charged_flag', None)
            if charged is True:
                if hasattr(item, 'charge'):
                    self.assertIn(item, fit.ordered)
                    charge = item.charge
                    self.assertIsNotNone(charge)
                    self.assertIs(charge.container, item)
                if hasattr(item, 'container'):
                    self.assertNotIn(item, fit.ordered)
                    container = item.container
                    self.assertIsNotNone(container)
                    self.assertIs(container.charge, item)
            elif charged is False:
                self.assertIn(item, fit.ordered)
                if hasattr(item, 'charge'):
                    self.assertIsNone(item.charge)
                if hasattr(item, 'container'):
                    self.assertIsNone(item.container)

        assertions = {
            ItemAdded: charge_relationship_assertion,
            ItemRemoved: charge_relationship_assertion
        }
        fit = Fit(self, message_assertions=assertions)
        fit.ordered = ItemList(fit, ModuleHigh)
        return fit

    def test_detached_module_none_to_none(self):
        module = ModuleHigh(1, state=State.active, charge=None)
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        self.assertIsNone(module._fit)

    def test_detached_module_none_to_free_charge(self):
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        # Action
        module.charge = charge
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)

    def test_detached_module_charge_to_free_charge(self):
        module = ModuleHigh(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Verification
        self.assertIs(module.charge, charge2)
        self.assertIsNone(charge1.container)
        self.assertIs(charge2.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge1._fit)
        self.assertIsNone(charge2._fit)

    def test_detached_module_charge_to_none(self):
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        # Action
        module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        self.assertIsNone(charge.container)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)

    def test_detached_module_none_to_non_charge(self):
        module = ModuleHigh(1, state=State.active, charge=None)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherItem(1))
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Verification
        self.assertIsNone(module.charge)
        self.assertIsNone(module._fit)
        self.assertIsNone(non_charge._fit)

    def test_detached_module_charge_to_non_charge(self):
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherItem(1))
        module.charge = charge
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        self.assertIsNone(non_charge._fit)

    def test_detached_module_none_to_bound_charge(self):
        fit_other = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        module_other = ModuleHigh(3, state=State.active, charge=None)
        charge_other = Charge(2)
        module_other.charge = charge_other
        fit_other.ordered.append(module_other)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIsNone(module._fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Cleanup
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_module_charge_to_bound_charge(self):
        fit_other = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        module_other = ModuleHigh(3, state=State.active, charge=None)
        charge_other = Charge(4)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Cleanup
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit_other)

    def test_fit_none_to_none(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        fit.ordered.append(module)
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module._fit, fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_none_to_free_charge(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            module.charge = charge
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_charge_to_free_charge(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        module.charge = charge1
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            module.charge = charge2
        # Verification
        self.assertIs(module.charge, charge2)
        self.assertIsNone(charge1.container)
        self.assertIs(charge2.container, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_charge_to_none(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        module.charge = charge
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            module.charge = None
        # Verification
        self.assertIsNone(module.charge)
        self.assertIsNone(charge.container)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_none_to_non_charge(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherItem(1))
        fit.ordered.append(module)
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module._fit, fit)
        self.assertIsNone(non_charge._fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_charge_to_non_charge(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherItem(1))
        fit.ordered.append(module)
        module.charge = charge
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIsNone(non_charge._fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_none_to_bound_charge(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        module_other = ModuleHigh(3, state=State.active, charge=None)
        charge_other = Charge(2)
        module_other.charge = charge_other
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Verification
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Cleanup
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_fit_charge_to_bound_charge(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        module_other = ModuleHigh(3, state=State.active, charge=None)
        charge_other = Charge(4)
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Verification
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Cleanup
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_fit_add_charged_module(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            fit.ordered.append(module)
        # Verification
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], module)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Cleanup
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_fit_remove_charged_module(self):
        fit = self.make_fit()
        module = ModuleHigh(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        fit.ordered.append(module)
        # Action
        with self.fit_assertions(fit), self.chargeable_assertions(charged=True):
            fit.ordered.remove(module)
        # Verification
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
