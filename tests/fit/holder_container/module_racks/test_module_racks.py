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

from eos.fit.holder.container import ModuleRacks
from tests.fit.fit_testcase import FitTestCase


class TestContainerModuleRacks(FitTestCase):

    def setUp(self):
        super().setUp()
        self.holder1 = Mock(spec_set=())
        self.holder2 = Mock(spec_set=())
        self.holder3 = Mock(spec_set=())
        self.holder4 = Mock(spec_set=())
        self.holder5 = Mock(spec_set=())
        self.holder6 = Mock(spec_set=())
        self.high_rack = [self.holder1, None, None, self.holder2]
        self.med_rack = [None, self.holder3, None, None, self.holder4]
        self.low_rack = [self.holder5, None, None, None, self.holder6]
        self.modules = ModuleRacks(high=self.high_rack, med=self.med_rack, low=self.low_rack)

    def test_rack_accessibility(self):
        self.assertIs(self.modules.high, self.high_rack)
        self.assertIs(self.modules.med, self.med_rack)
        self.assertIs(self.modules.low, self.low_rack)

    def test_holders_len(self):
        module_holders = self.modules.holders()
        self.assertEqual(len(module_holders), 6)
        self.high_rack.remove(self.holder1)
        self.assertEqual(len(module_holders), 5)
        self.med_rack.remove(self.holder3)
        self.assertEqual(len(module_holders), 4)
        self.low_rack.append(self.holder1)
        self.assertEqual(len(module_holders), 5)

    def test_holders_iter(self):
        module_holders = self.modules.holders()
        expected = [
            self.holder1, self.holder2, self.holder3,
            self.holder4, self.holder5, self.holder6
        ]
        self.assertEqual(list(module_holders), expected)
        self.high_rack.remove(self.holder1)
        expected = [
            self.holder2, self.holder3, self.holder4,
            self.holder5, self.holder6
        ]
        self.assertEqual(list(module_holders), expected)
        self.med_rack.remove(self.holder3)
        expected = [
            self.holder2, self.holder4, self.holder5,
            self.holder6
        ]
        self.assertEqual(list(module_holders), expected)
        self.low_rack.append(self.holder1)
        expected = [
            self.holder2, self.holder4, self.holder5,
            self.holder6, self.holder1
        ]
        self.assertEqual(list(module_holders), expected)

    def test_holder_contains(self):
        module_holders = self.modules.holders()
        self.assertFalse(None in module_holders)
        self.assertTrue(self.holder1 in module_holders)
        self.assertTrue(self.holder2 in module_holders)
        self.high_rack.remove(self.holder1)
        self.assertFalse(self.holder1 in module_holders)
        self.assertTrue(self.holder2 in module_holders)
        self.assertTrue(self.holder3 in module_holders)
        self.assertTrue(self.holder4 in module_holders)
        self.med_rack.remove(self.holder3)
        self.assertFalse(self.holder3 in module_holders)
        self.assertTrue(self.holder4 in module_holders)
        self.assertTrue(self.holder5 in module_holders)
        self.assertTrue(self.holder6 in module_holders)
        self.assertFalse(self.holder1 in module_holders)
        self.low_rack.append(self.holder1)
        self.assertTrue(self.holder5 in module_holders)
        self.assertTrue(self.holder6 in module_holders)
        self.assertTrue(self.holder1 in module_holders)
        self.assertFalse(None in module_holders)
