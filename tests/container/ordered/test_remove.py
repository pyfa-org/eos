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
from eos.fit.message import ItemAdded, ItemRemoved
from tests.container.environment import Fit, Item
from tests.container.container_testcase import ContainerTestCase


class TestContainerOrderedRemove(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIn(m.item, f.container),
            ItemRemoved: lambda f, m: self.assertIn(m.item, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = ItemList(fit, Item)
        return fit

    def test_item(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.online, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.online, spec_set=Item(1))
        fit.container.append(item1)
        fit.container.append(item2)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(item1)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item2)
        self.assertIsNone(item1._fit)
        self.assertIs(item2._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(item2)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_after_nones(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.overload, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.active, spec_set=Item(1))
        item3 = Mock(_fit=None, state=State.overload, spec_set=Item(1))
        fit.container.append(item1)
        fit.container.place(3, item2)
        fit.container.place(6, item3)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(item2)
        # Verification
        self.assertIs(len(fit.container), 6)
        self.assertIs(fit.container[0], item1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIs(fit.container[5], item3)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIs(item3._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(item3)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIsNone(item3._fit)
        # Cleanup
        fit.container.remove(item1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_failure(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.online, spec_set=Item(1))
        fit.container.append(item1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.remove, item2)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        fit.container.remove(item1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.remove, item1)
        # checks
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_none(self):
        # Check that first found None is removed
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.active, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        fit.container.place(1, item1)
        fit.container.place(3, item2)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(None)
        # Verification
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], item1)
        self.assertIsNone(fit.container[1])
        self.assertIs(fit.container[2], item2)
        self.assertIs(item1._fit, fit)
        self.assertIs(item2._fit, fit)
        # Cleanup
        fit.container.remove(item1)
        fit.container.remove(item2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_none_failure(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.overload, spec_set=Item(1))
        fit.container.append(item)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.remove, None)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item)
        self.assertIs(item._fit, fit)
        # Cleanup
        fit.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_item(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.active, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.overload, spec_set=Item(1))
        fit.container.append(item1)
        fit.container.append(item2)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(0)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item2)
        self.assertIsNone(item1._fit)
        self.assertIs(item2._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(0)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_none(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.online, spec_set=Item(1))
        fit.container.place(1, item)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(0)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item)
        self.assertIs(item._fit, fit)
        # Cleanup
        fit.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_after_nones(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.online, spec_set=Item(1))
        item3 = Mock(_fit=None, state=State.active, spec_set=Item(1))
        fit.container.append(item1)
        fit.container.place(3, item2)
        fit.container.place(6, item3)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(3)
        # Verification
        self.assertIs(len(fit.container), 6)
        self.assertIs(fit.container[0], item1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIs(fit.container[5], item3)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIs(item3._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(5)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        self.assertIsNone(item3._fit)
        # Cleanup
        fit.container.remove(item1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_outside(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        fit.container.append(item)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(IndexError, fit.container.remove, 5)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item)
        self.assertIs(item._fit, fit)
        # Cleanup
        fit.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
