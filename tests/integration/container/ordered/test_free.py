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
from tests.integration.container.container_testcase import ContainerTestCase


class TestContainerOrderedFree(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIn(m.item, f.container),
            ItemRemoved: lambda f, m: self.assertIn(m.item, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = ItemList(fit, Item)
        return fit

    def test_none(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.append(item2)
        # Action
        self.assertRaises(ValueError, fit.container.free, None)
        # Verification
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], item1)
        self.assertIs(fit.container[1], item2)
        self.assertIs(item1._fit, fit)
        self.assertIs(item2._fit, fit)
        # Cleanup
        fit.container.free(item1)
        # Action
        fit.container.free(None)
        # Verification
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], item2)
        self.assertIsNone(item1._fit)
        self.assertIs(item2._fit, fit)
        # Cleanup
        fit.container.free(item2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.append(item2)
        # Action
        fit.container.free(item1)
        # Verification
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], item2)
        self.assertIsNone(item1._fit)
        self.assertIs(item2._fit, fit)
        # Action
        fit.container.free(item2)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_failure(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        fit.container.append(item1)
        # Action
        self.assertRaises(ValueError, fit.container.free, item2)
        # Verification
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        fit.container.free(item1)
        # Action
        self.assertRaises(ValueError, fit.container.free, item1)
        # Verification
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_after_nones(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        item3 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.place(3, item2)
        fit.container.place(6, item3)
        # Action
        fit.container.free(item2)
        # Verification
        self.assertEqual(len(fit.container), 7)
        self.assertIs(fit.container[0], item1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIsNone(fit.container[5])
        self.assertIs(fit.container[6], item3)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIs(item3._fit, fit)
        # Action
        fit.container.free(item3)
        # Verification
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIsNone(item3._fit)
        # Cleanup
        fit.container.free(item1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_item(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.append(item2)
        # Action
        fit.container.free(0)
        # Verification
        self.assertEqual(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], item2)
        self.assertIsNone(item1._fit)
        self.assertIs(item2._fit, fit)
        # Action
        fit.container.free(1)
        # Verification
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_none(self):
        item = Item(self.ch.type().id)
        fit.container.place(1, item)
        # Action
        fit.container.free(0)
        # Verification
        self.assertEqual(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], item)
        self.assertIs(item._fit, fit)
        # Cleanup
        fit.container.free(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_after_nones(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        item3 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.place(3, item2)
        fit.container.place(6, item3)
        # Action
        fit.container.free(3)
        # Verification
        self.assertEqual(len(fit.container), 7)
        self.assertIs(fit.container[0], item1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIsNone(fit.container[5])
        self.assertIs(fit.container[6], item3)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIs(item3._fit, fit)
        # Action
        fit.container.free(6)
        # Verification
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIsNone(item3._fit)
        # Cleanup
        fit.container.free(item1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_outside(self):
        item = Item(self.ch.type().id)
        fit.container.append(item)
        # Action
        self.assertRaises(IndexError, fit.container.free, 5)
        # Verification
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], item)
        self.assertIs(item._fit, fit)
        # Cleanup
        fit.container.free(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
