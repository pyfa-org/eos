#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from unittest.mock import Mock

from eos.const.eos import State
from eos.fit.holder.container import HolderList
from eos.fit.holder.item import Charge, Implant, Module
from eos.tests.fit.fit_testcase import FitTestCase


class TestModuleCharge(FitTestCase):
    """
    Everything related to charge switching is tested here.
    """

    def setUp(self):
        FitTestCase.setUp(self)
        # This variable will control check of
        # module <-> charge link
        self.expect_module_charge_link = None

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.ordered = HolderList(fit, Module)
        return fit

    def custom_membership_check(self, fit, holder):
        # If link variable is True, we make sure
        # there's link between module and charge upon
        # addition to both of trackers. If False, we
        # ensure there's no link.
        if self.expect_module_charge_link is True:
            if hasattr(holder, 'charge'):
                self.assertIn(holder, fit.ordered)
                charge = holder.charge
                self.assertIsNotNone(charge)
                self.assertIs(charge.container, holder)
                other = holder._other
                self.assertIs(other, charge)
                self.assertIs(other._other, holder)
            if hasattr(holder, 'container'):
                self.assertNotIn(holder, fit.ordered)
                container = holder.container
                self.assertIsNotNone(container)
                self.assertIs(container.charge, holder)
                other = holder._other
                self.assertIs(other, container)
                self.assertIs(other._other, holder)
        elif self.expect_module_charge_link is False:
            self.assertIn(holder, fit.ordered)
            if hasattr(holder, 'charge'):
                self.assertIsNone(holder.charge)
            if hasattr(holder, 'container'):
                self.assertIsNone(holder.container)
            self.assertIsNone(holder._other)

    def test_detached_module_none_to_none(self):
        module = Module(1, state=State.active, charge=None)
        # Action
        module.charge = None
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(module._fit)

    def test_detached_module_none_to_free_charge(self):
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        # Action
        module.charge = charge
        # Checks
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)

    def test_detached_module_charge_to_free_charge(self):
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Checks
        self.assertIs(module.charge, charge2)
        self.assertIs(module._other, charge2)
        self.assertIsNone(charge1.container)
        self.assertIsNone(charge1._other)
        self.assertIs(charge2.container, module)
        self.assertIs(charge2._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge1._fit)
        self.assertIsNone(charge2._fit)

    def test_detached_module_charge_to_none(self):
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        # Action
        module.charge = None
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)

    def test_detached_module_none_to_non_charge(self):
        module = Module(1, state=State.active, charge=None)
        non_charge = Implant(2)
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(module._fit)
        self.assertIsNone(non_charge._fit)

    def test_detached_module_charge_to_non_charge(self):
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        non_charge = Implant(3)
        module.charge = charge
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        self.assertIsNone(non_charge._fit)

    def test_detached_module_none_to_bound_charge(self):
        fit_other = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        module_other = Module(3, state=State.active, charge=None)
        charge_other = Charge(2)
        module_other.charge = charge_other
        fit_other.ordered.append(module_other)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(module_other._other, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(charge_other._other, module_other)
        self.assertIsNone(module._fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Misc
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_module_charge_to_bound_charge(self):
        fit_other = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module_other = Module(3, state=State.active, charge=None)
        charge_other = Charge(4)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(module_other._other, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(charge_other._other, module_other)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Misc
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_fit_none_to_none(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        fit.ordered.append(module)
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_none_to_free_charge(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        # Action
        module.charge = charge
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_charge_to_free_charge(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(module.charge, charge2)
        self.assertIs(module._other, charge2)
        self.assertIsNone(charge1.container)
        self.assertIsNone(charge1._other)
        self.assertIs(charge2.container, module)
        self.assertIs(charge2._other, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_charge_to_none(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        module.charge = charge
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_none_to_non_charge(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        non_charge = Implant(2)
        fit.ordered.append(module)
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module._fit, fit)
        self.assertIsNone(non_charge._fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_charge_to_non_charge(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        non_charge = Implant(3)
        fit.ordered.append(module)
        module.charge = charge
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIsNone(non_charge._fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_none_to_bound_charge(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        module_other = Module(3, state=State.active, charge=None)
        charge_other = Charge(2)
        module_other.charge = charge_other
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(module_other._other, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(charge_other._other, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Misc
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_fit_charge_to_bound_charge(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module_other = Module(3, state=State.active, charge=None)
        charge_other = Charge(4)
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(module_other._other, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(charge_other._other, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Misc
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_fit_add_charged_module(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        # Action
        fit.ordered.append(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], module)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_remove_charged_module(self):
        fit = self.make_fit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        fit.ordered.append(module)
        # Action
        fit.ordered.remove(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_none(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        fit.ordered.append(module)
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_free_charge(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        self.expect_module_charge_link = True
        # Action
        module.charge = charge
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.lt)
        self.assertEqual(fit.lt[charge], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.rt)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.st)
        self.assertEqual(fit.st[charge], {State.offline})
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_charge_to_free_charge(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        module.charge = charge1
        self.expect_module_charge_link = True
        # Action
        module.charge = charge2
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge2, fit.lt)
        self.assertEqual(fit.lt[charge2], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge2, fit.rt)
        self.assertEqual(fit.rt[charge2], {State.offline})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIn(charge2, fit.st)
        self.assertEqual(fit.st[charge2], {State.offline})
        self.assertIs(module.charge, charge2)
        self.assertIs(module._other, charge2)
        self.assertIsNone(charge1.container)
        self.assertIsNone(charge1._other)
        self.assertIs(charge2.container, module)
        self.assertIs(charge2._other, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_charge_to_none(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        module.charge = charge
        self.expect_module_charge_link = True
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_non_charge(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        non_charge = Implant(2)
        fit.ordered.append(module)
        self.expect_module_charge_link = True
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(len(fit.st), 1)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module._fit, fit)
        self.assertIsNone(non_charge._fit)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_charge_to_non_charge(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        non_charge = Implant(3)
        fit.ordered.append(module)
        module.charge = charge
        self.expect_module_charge_link = True
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.lt)
        self.assertEqual(fit.lt[charge], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.rt)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.st)
        self.assertEqual(fit.st[charge], {State.offline})
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIsNone(non_charge._fit)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_bound_charge(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        module_other = Module(3, state=State.active, charge=None)
        charge_other = Charge(2)
        module_other.charge = charge_other
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        self.expect_module_charge_link = True
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit_other.lt), 2)
        self.assertIn(module_other, fit_other.lt)
        self.assertEqual(fit_other.lt[module_other], {State.offline, State.online, State.active})
        self.assertIn(charge_other, fit_other.lt)
        self.assertEqual(fit_other.lt[charge_other], {State.offline})
        self.assertEqual(len(fit_other.rt), 2)
        self.assertIn(module_other, fit_other.rt)
        self.assertEqual(fit_other.rt[module_other], {State.offline, State.online, State.active})
        self.assertIn(charge_other, fit_other.rt)
        self.assertEqual(fit_other.rt[charge_other], {State.offline})
        self.assertEqual(len(fit_other.st), 2)
        self.assertIn(module_other, fit_other.st)
        self.assertEqual(fit_other.st[module_other], {State.offline, State.online, State.active})
        self.assertIn(charge_other, fit_other.st)
        self.assertEqual(fit_other.st[charge_other], {State.offline})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(module_other._other, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(charge_other._other, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_fit_charge_to_bound_charge(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module_other = Module(3, state=State.active, charge=None)
        charge_other = Charge(4)
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        self.expect_module_charge_link = True
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.lt)
        self.assertEqual(fit.lt[charge], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.rt)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.st)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertEqual(len(fit_other.lt), 2)
        self.assertIn(module_other, fit_other.lt)
        self.assertEqual(fit_other.lt[module_other], {State.offline, State.online, State.active})
        self.assertIn(charge_other, fit_other.lt)
        self.assertEqual(fit_other.lt[charge_other], {State.offline})
        self.assertEqual(len(fit_other.rt), 2)
        self.assertIn(module_other, fit_other.rt)
        self.assertEqual(fit_other.rt[module_other], {State.offline, State.online, State.active})
        self.assertIn(charge_other, fit_other.rt)
        self.assertEqual(fit_other.rt[charge_other], {State.offline})
        self.assertEqual(len(fit_other.st), 2)
        self.assertIn(module_other, fit_other.st)
        self.assertEqual(fit_other.st[module_other], {State.offline, State.online, State.active})
        self.assertIn(charge_other, fit_other.st)
        self.assertEqual(fit_other.st[charge_other], {State.offline})
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(module_other._other, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(charge_other._other, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_fit_add_charged_module(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        self.expect_module_charge_link = True
        # Action
        fit.ordered.append(module)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.lt)
        self.assertEqual(fit.lt[charge], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.rt)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(module, fit.st)
        self.assertEqual(fit.st[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.st)
        self.assertEqual(fit.st[charge], {State.offline})
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], module)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_remove_charged_module(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        fit.ordered.append(module)
        self.expect_module_charge_link = True
        # Action
        fit.ordered.remove(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
