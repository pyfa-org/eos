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


class TestContainerModuleRacks(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.mod_high1 = ModuleHigh(self.mktype().id)
        self.mod_high2 = ModuleHigh(self.mktype().id)
        self.mod_med1 = ModuleMed(self.mktype().id)
        self.mod_med2 = ModuleMed(self.mktype().id)
        self.mod_low1 = ModuleLow(self.mktype().id)
        self.mod_low2 = ModuleLow(self.mktype().id)
        self.mod_low3 = ModuleLow(self.mktype().id)
        self.fit = Fit()
        self.fit.modules.high.place(0, self.mod_high1)
        self.fit.modules.high.place(3, self.mod_high2)
        self.fit.modules.med.place(1, self.mod_med1)
        self.fit.modules.med.place(4, self.mod_med2)
        self.fit.modules.low.place(0, self.mod_low1)
        self.fit.modules.low.place(4, self.mod_low2)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_items_len(self):
        module_items = self.fit.modules.items()
        self.assertEqual(len(module_items), 6)
        self.fit.modules.high.remove(self.mod_high1)
        self.assertEqual(len(module_items), 5)
        self.fit.modules.med.remove(self.mod_med1)
        self.assertEqual(len(module_items), 4)
        self.fit.modules.low.append(self.mod_low3)
        self.assertEqual(len(module_items), 5)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_items_iter(self):
        module_items = self.fit.modules.items()
        expected = [
            self.mod_high1, self.mod_high2,
            self.mod_med1, self.mod_med2,
            self.mod_low1, self.mod_low2]
        self.assertEqual(list(module_items), expected)
        self.fit.modules.high.remove(self.mod_high1)
        expected = [
            self.mod_high2, self.mod_med1,
            self.mod_med2,
            self.mod_low1, self.mod_low2]
        self.assertEqual(list(module_items), expected)
        self.fit.modules.med.remove(self.mod_med1)
        expected = [
            self.mod_high2,
            self.mod_med2,
            self.mod_low1, self.mod_low2]
        self.assertEqual(list(module_items), expected)
        self.fit.modules.low.append(self.mod_low3)
        expected = [
            self.mod_high2,
            self.mod_med2,
            self.mod_low1, self.mod_low2, self.mod_low3]
        self.assertEqual(list(module_items), expected)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)

    def test_item_contains(self):
        module_items = self.fit.modules.items()
        self.assertFalse(None in module_items)
        self.assertTrue(self.mod_high1 in module_items)
        self.assertTrue(self.mod_high2 in module_items)
        self.fit.modules.high.remove(self.mod_high1)
        self.assertFalse(self.mod_high1 in module_items)
        self.assertTrue(self.mod_high2 in module_items)
        self.assertTrue(self.mod_med1 in module_items)
        self.assertTrue(self.mod_med2 in module_items)
        self.fit.modules.med.remove(self.mod_med1)
        self.assertFalse(self.mod_med1 in module_items)
        self.assertTrue(self.mod_med2 in module_items)
        self.assertTrue(self.mod_low1 in module_items)
        self.assertTrue(self.mod_low2 in module_items)
        self.assertFalse(self.mod_low3 in module_items)
        self.fit.modules.low.append(self.mod_low3)
        self.assertTrue(self.mod_low1 in module_items)
        self.assertTrue(self.mod_low2 in module_items)
        self.assertTrue(self.mod_low3 in module_items)
        self.assertFalse(None in module_items)
        # Cleanup
        self.assertEqual(len(self.get_log()), 0)
