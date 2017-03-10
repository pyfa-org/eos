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


class TestContainerOrderedMisc(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIn(m.item, f.container),
            ItemRemoved: lambda f, m: self.assertIn(m.item, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = ItemList(fit, Item)
        return fit

    def test_len(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        self.assertEqual(len(fit.container), 0)
        fit.container.append(item1)
        self.assertEqual(len(fit.container), 1)
        fit.container.place(3, item2)
        self.assertEqual(len(fit.container), 4)
        fit.container.remove(item1)
        self.assertEqual(len(fit.container), 3)
        fit.container.remove(item2)
        self.assertEqual(len(fit.container), 0)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_contains(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        self.assertFalse(item1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(item2 in fit.container)
        fit.container.append(item1)
        self.assertTrue(item1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(item2 in fit.container)
        fit.container.place(3, item2)
        self.assertTrue(item1 in fit.container)
        self.assertTrue(None in fit.container)
        self.assertTrue(item2 in fit.container)
        fit.container.remove(item1)
        self.assertFalse(item1 in fit.container)
        self.assertTrue(None in fit.container)
        self.assertTrue(item2 in fit.container)
        fit.container.remove(item2)
        self.assertFalse(item1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(item2 in fit.container)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_iter(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        self.assertEqual(list(item for item in fit.container), [])
        fit.container.append(item1)
        self.assertEqual(list(item for item in fit.container), [item1])
        fit.container.place(3, item2)
        self.assertEqual(list(item for item in fit.container), [item1, None, None, item2])
        fit.container.remove(item1)
        self.assertEqual(list(item for item in fit.container), [None, None, item2])
        fit.container.remove(item2)
        self.assertEqual(list(item for item in fit.container), [])
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_clear(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.place(3, item2)
        # Action
        fit.container.clear()
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_slice(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        fit.container.append(item1)
        fit.container.place(3, item2)
        slice_full = fit.container[:]
        self.assertEqual(len(slice_full), 4)
        self.assertIs(slice_full[0], item1)
        self.assertIsNone(slice_full[1])
        self.assertIsNone(slice_full[2])
        self.assertIs(slice_full[3], item2)
        slice_positive = fit.container[0:2]
        self.assertEqual(len(slice_positive), 2)
        self.assertIs(slice_positive[0], item1)
        self.assertIsNone(slice_positive[1])
        slice_negative = fit.container[-2:]
        self.assertEqual(len(slice_negative), 2)
        self.assertIsNone(slice_negative[0])
        self.assertIs(slice_negative[1], item2)
        slice_step = fit.container[::2]
        self.assertEqual(len(slice_step), 2)
        self.assertIs(slice_step[0], item1)
        self.assertIsNone(slice_step[1])
        fit.container.remove(item1)
        fit.container.remove(item2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_view(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        view = fit.container.items()
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(item1 in view)
        self.assertFalse(item2 in view)
        self.assertFalse(None in view)
        fit.container.append(item1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [item1])
        self.assertTrue(item1 in view)
        self.assertFalse(item2 in view)
        self.assertFalse(None in view)
        fit.container.place(3, item2)
        self.assertEqual(len(view), 2)
        self.assertEqual(list(view), [item1, item2])
        self.assertTrue(item1 in view)
        self.assertTrue(item2 in view)
        self.assertFalse(None in view)
        fit.container.free(item1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [item2])
        self.assertFalse(item1 in view)
        self.assertTrue(item2 in view)
        self.assertFalse(None in view)
        fit.container.free(item2)
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(item1 in view)
        self.assertFalse(item2 in view)
        self.assertFalse(None in view)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
