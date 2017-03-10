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

from eos.fit.container import ModuleRacks
from tests.integration.container.container_testcase import ContainerTestCase


class TestContainerModuleRacks(ContainerTestCase):

    def setUp(self):
        super().setUp()
        self.item1 = Mock(spec_set=())
        self.item2 = Mock(spec_set=())
        self.item3 = Mock(spec_set=())
        self.item4 = Mock(spec_set=())
        self.item5 = Mock(spec_set=())
        self.item6 = Mock(spec_set=())
        self.high_rack = [self.item1, None, None, self.item2]
        self.med_rack = [None, self.item3, None, None, self.item4]
        self.low_rack = [self.item5, None, None, None, self.item6]
        self.modules = ModuleRacks(high=self.high_rack, med=self.med_rack, low=self.low_rack)

    def test_rack_accessibility(self):
        self.assertIs(self.modules.high, self.high_rack)
        self.assertIs(self.modules.med, self.med_rack)
        self.assertIs(self.modules.low, self.low_rack)

    def test_items_len(self):
        module_items = self.modules.items()
        self.assertEqual(len(module_items), 6)
        self.high_rack.remove(self.item1)
        self.assertEqual(len(module_items), 5)
        self.med_rack.remove(self.item3)
        self.assertEqual(len(module_items), 4)
        self.low_rack.append(self.item1)
        self.assertEqual(len(module_items), 5)

    def test_items_iter(self):
        module_items = self.modules.items()
        expected = [
            self.item1, self.item2, self.item3,
            self.item4, self.item5, self.item6
        ]
        self.assertEqual(list(module_items), expected)
        self.high_rack.remove(self.item1)
        expected = [
            self.item2, self.item3, self.item4,
            self.item5, self.item6
        ]
        self.assertEqual(list(module_items), expected)
        self.med_rack.remove(self.item3)
        expected = [
            self.item2, self.item4, self.item5,
            self.item6
        ]
        self.assertEqual(list(module_items), expected)
        self.low_rack.append(self.item1)
        expected = [
            self.item2, self.item4, self.item5,
            self.item6, self.item1
        ]
        self.assertEqual(list(module_items), expected)

    def test_item_contains(self):
        module_items = self.modules.items()
        self.assertFalse(None in module_items)
        self.assertTrue(self.item1 in module_items)
        self.assertTrue(self.item2 in module_items)
        self.high_rack.remove(self.item1)
        self.assertFalse(self.item1 in module_items)
        self.assertTrue(self.item2 in module_items)
        self.assertTrue(self.item3 in module_items)
        self.assertTrue(self.item4 in module_items)
        self.med_rack.remove(self.item3)
        self.assertFalse(self.item3 in module_items)
        self.assertTrue(self.item4 in module_items)
        self.assertTrue(self.item5 in module_items)
        self.assertTrue(self.item6 in module_items)
        self.assertFalse(self.item1 in module_items)
        self.low_rack.append(self.item1)
        self.assertTrue(self.item5 in module_items)
        self.assertTrue(self.item6 in module_items)
        self.assertTrue(self.item1 in module_items)
        self.assertFalse(None in module_items)
