# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
from eos.data.source import Source
from eos.fit.holder.container import HolderList
from tests.fit.environment import CachingCharge, CachingModule, OtherCachingHolder
from tests.fit.fit_testcase import FitTestCase


class TestModuleCharge(FitTestCase):
    """
    Everything related to charge switching is tested here.
    """

    def setUp(self):
        super().setUp()
        # This variable will control check of
        # module <-> charge link
        self.expect_module_charge_link = None

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.ordered = HolderList(fit, CachingModule)
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
            if hasattr(holder, 'container'):
                self.assertNotIn(holder, fit.ordered)
                container = holder.container
                self.assertIsNotNone(container)
                self.assertIs(container.charge, holder)
        elif self.expect_module_charge_link is False:
            self.assertIn(holder, fit.ordered)
            if hasattr(holder, 'charge'):
                self.assertIsNone(holder.charge)
            if hasattr(holder, 'container'):
                self.assertIsNone(holder.container)

    def test_detached_module_none_to_none(self):
        module = CachingModule(1, state=State.active, charge=None)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = None
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._fit)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)

    def test_detached_module_none_to_free_charge(self):
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = charge
        # Checks
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)

    def test_detached_module_charge_to_free_charge(self):
        module = CachingModule(1, state=State.active, charge=None)
        charge1 = CachingCharge(2)
        charge2 = CachingCharge(3)
        module.charge = charge1
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge1_cleans_before = len(charge1._clear_volatile_attrs.mock_calls)
        charge2_cleans_before = len(charge2._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = charge2
        # Checks
        self.assertIs(module.charge, charge2)
        self.assertIsNone(charge1.container)
        self.assertIs(charge2.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge1._fit)
        self.assertIsNone(charge2._fit)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge1_cleans_after = len(charge1._clear_volatile_attrs.mock_calls)
        charge2_cleans_after = len(charge2._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge1_cleans_after - charge1_cleans_before, 0)
        self.assertEqual(charge2_cleans_after - charge2_cleans_before, 0)

    def test_detached_module_charge_to_none(self):
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module.charge = charge
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = None
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(charge.container)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)

    def test_detached_module_none_to_non_charge(self):
        module = CachingModule(1, state=State.active, charge=None)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        non_charge_cleans_before = len(non_charge._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._fit)
        self.assertIsNone(non_charge._fit)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        non_charge_cleans_after = len(non_charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(non_charge_cleans_after - non_charge_cleans_before, 0)

    def test_detached_module_charge_to_non_charge(self):
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        module.charge = charge
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        non_charge_cleans_before = len(non_charge._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        self.assertIsNone(non_charge._fit)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        non_charge_cleans_after = len(non_charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        self.assertEqual(non_charge_cleans_after - non_charge_cleans_before, 0)

    def test_detached_module_none_to_bound_charge(self):
        fit_other = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        module_other = CachingModule(3, state=State.active, charge=None)
        charge_other = CachingCharge(2)
        module_other.charge = charge_other
        fit_other.ordered.append(module_other)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_before = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_before = len(charge_other._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIsNone(module.charge)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIsNone(module._fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_after = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_after = len(charge_other._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        self.assertEqual(module_other_cleans_after - module_other_cleans_before, 0)
        self.assertEqual(charge_other_cleans_after - charge_other_cleans_before, 0)
        # Misc
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_module_charge_to_bound_charge(self):
        fit_other = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module_other = CachingModule(3, state=State.active, charge=None)
        charge_other = CachingCharge(4)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_before = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_before = len(charge_other._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge_other)
        # Checks
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_after = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_after = len(charge_other._clear_volatile_attrs.mock_calls)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        self.assertEqual(module_other_cleans_after - module_other_cleans_before, 0)
        self.assertEqual(charge_other_cleans_after - charge_other_cleans_before, 0)
        # Misc
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_fit_none_to_none(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        fit.ordered.append(module)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(module.charge)
        self.assertIs(module._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_none_to_free_charge(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        fit.ordered.append(module)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = charge
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_charge_to_free_charge(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge1 = CachingCharge(2)
        charge2 = CachingCharge(3)
        fit.ordered.append(module)
        module.charge = charge1
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge1_cleans_before = len(charge1._clear_volatile_attrs.mock_calls)
        charge2_cleans_before = len(charge2._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = charge2
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(module.charge, charge2)
        self.assertIsNone(charge1.container)
        self.assertIs(charge2.container, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge1_cleans_after = len(charge1._clear_volatile_attrs.mock_calls)
        charge2_cleans_after = len(charge2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge1_cleans_after - charge1_cleans_before, 0)
        self.assertEqual(charge2_cleans_after - charge2_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_charge_to_none(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        fit.ordered.append(module)
        module.charge = charge
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(charge.container)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_none_to_non_charge(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        fit.ordered.append(module)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        non_charge_cleans_before = len(non_charge._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(module.charge)
        self.assertIs(module._fit, fit)
        self.assertIsNone(non_charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        non_charge_cleans_after = len(non_charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(non_charge_cleans_after - non_charge_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_charge_to_non_charge(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        fit.ordered.append(module)
        module.charge = charge
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        non_charge_cleans_before = len(non_charge._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, module.__setattr__, 'charge', non_charge)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIsNone(non_charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        non_charge_cleans_after = len(non_charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        self.assertEqual(non_charge_cleans_after - non_charge_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_none_to_bound_charge(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        module_other = CachingModule(3, state=State.active, charge=None)
        charge_other = CachingCharge(2)
        module_other.charge = charge_other
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_before = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_before = len(charge_other._clear_volatile_attrs.mock_calls)
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
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_after = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_after = len(charge_other._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        self.assertEqual(module_other_cleans_after - module_other_cleans_before, 0)
        self.assertEqual(charge_other_cleans_after - charge_other_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_fit_charge_to_bound_charge(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module_other = CachingModule(3, state=State.active, charge=None)
        charge_other = CachingCharge(4)
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_before = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_before = len(charge_other._clear_volatile_attrs.mock_calls)
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
        self.assertIs(charge.container, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_after = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_after = len(charge_other._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        self.assertEqual(module_other_cleans_after - module_other_cleans_before, 0)
        self.assertEqual(charge_other_cleans_after - charge_other_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_fit_add_charged_module(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module.charge = charge
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        fit.ordered.append(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], module)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_detached_fit_remove_charged_module(self):
        fit = self.make_fit()
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module.charge = charge
        fit.ordered.append(module)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        fit.ordered.remove(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_none(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        fit.ordered.append(module)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
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
        self.assertIs(module._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        # Misc
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_free_charge(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        fit.ordered.append(module)
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
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
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(module_cleans_after - module_cleans_before, 1)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 1)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_charge_to_free_charge(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge1 = CachingCharge(2)
        charge2 = CachingCharge(3)
        fit.ordered.append(module)
        module.charge = charge1
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge1_cleans_before = len(charge1._clear_volatile_attrs.mock_calls)
        charge2_cleans_before = len(charge2._clear_volatile_attrs.mock_calls)
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
        self.assertIsNone(charge1.container)
        self.assertIs(charge2.container, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge1_cleans_after = len(charge1._clear_volatile_attrs.mock_calls)
        charge2_cleans_after = len(charge2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 2)
        self.assertEqual(module_cleans_after - module_cleans_before, 2)
        self.assertEqual(charge1_cleans_after - charge1_cleans_before, 1)
        self.assertEqual(charge2_cleans_after - charge2_cleans_before, 1)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_charge_to_none(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        fit.ordered.append(module)
        module.charge = charge
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
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
        self.assertIsNone(charge.container)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(module_cleans_after - module_cleans_before, 1)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 1)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_non_charge(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        fit.ordered.append(module)
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        non_charge_cleans_before = len(non_charge._clear_volatile_attrs.mock_calls)
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
        self.assertIs(module._fit, fit)
        self.assertIsNone(non_charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        non_charge_cleans_after = len(non_charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(non_charge_cleans_after - non_charge_cleans_before, 0)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_charge_to_non_charge(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        non_charge = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        fit.ordered.append(module)
        module.charge = charge
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        non_charge_cleans_before = len(non_charge._clear_volatile_attrs.mock_calls)
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
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIsNone(non_charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        non_charge_cleans_after = len(non_charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        self.assertEqual(non_charge_cleans_after - non_charge_cleans_before, 0)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_none_to_bound_charge(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        fit_other = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        module_other = CachingModule(3, state=State.active, charge=None)
        charge_other = CachingCharge(2)
        module_other.charge = charge_other
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_before = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_before = len(charge_other._clear_volatile_attrs.mock_calls)
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
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_after = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_after = len(charge_other._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        self.assertEqual(module_other_cleans_after - module_other_cleans_before, 0)
        self.assertEqual(charge_other_cleans_after - charge_other_cleans_before, 0)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_fit_charge_to_bound_charge(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        fit_other = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module_other = CachingModule(3, state=State.active, charge=None)
        charge_other = CachingCharge(4)
        fit.ordered.append(module)
        fit_other.ordered.append(module_other)
        module.charge = charge
        module_other.charge = charge_other
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_before = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_before = len(charge_other._clear_volatile_attrs.mock_calls)
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
        self.assertIs(charge.container, module)
        self.assertIs(module_other.charge, charge_other)
        self.assertIs(charge_other.container, module_other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        self.assertIs(module_other._fit, fit_other)
        self.assertIs(charge_other._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        module_other_cleans_after = len(module_other._clear_volatile_attrs.mock_calls)
        charge_other_cleans_after = len(charge_other._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(module_cleans_after - module_cleans_before, 0)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        self.assertEqual(module_other_cleans_after - module_other_cleans_before, 0)
        self.assertEqual(charge_other_cleans_after - charge_other_cleans_before, 0)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        fit_other.ordered.remove(module_other)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_fit_add_charged_module(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module.charge = charge
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
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
        self.assertIs(charge.container, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(module_cleans_after - module_cleans_before, 1)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 1)
        # Misc
        self.expect_module_charge_link = None
        fit.ordered.remove(module)
        self.assert_fit_buffers_empty(fit)

    def test_attached_fit_remove_charged_module(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        module = CachingModule(1, state=State.active, charge=None)
        charge = CachingCharge(2)
        module.charge = charge
        fit.ordered.append(module)
        self.expect_module_charge_link = True
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_before = len(charge._clear_volatile_attrs.mock_calls)
        # Action
        fit.ordered.remove(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(charge.container, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(module._clear_volatile_attrs.mock_calls)
        charge_cleans_after = len(charge._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(module_cleans_after - module_cleans_before, 1)
        self.assertEqual(charge_cleans_after - charge_cleans_before, 1)
        # Misc
        self.assert_fit_buffers_empty(fit)
