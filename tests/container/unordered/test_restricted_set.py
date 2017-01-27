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
from eos.fit.container import ItemRestrictedSet
from eos.fit.messages import ItemAdded, ItemRemoved
from tests.container.environment import Fit, Item, OtherItem
from tests.container.container_testcase import ContainerTestCase


class TestContainerRestrictedSet(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIn(m.item, f.container),
            ItemRemoved: lambda f, m: self.assertIn(m.item, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = ItemRestrictedSet(fit, Item)
        return fit

    def test_add_none(self):
        fit = self.make_fit()
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_add_item(self):
        fit = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.offline, spec_set=Item(1))
        # Action
        with self.fit_assertions(fit):
            fit.container.add(item)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], item)
        self.assertIn(item, fit.container)
        self.assertIs(item._fit, fit)
        # Misc
        fit.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_add_item_type_failure(self):
        fit = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.offline, spec_set=OtherItem(1))
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.add, item)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_add_item_value_failure_has_fit(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.overload, spec_set=Item(1))
        fit_other.container.add(item)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.add, item)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fit_other.container), 1)
        self.assertIs(fit_other.container[1], item)
        self.assertIn(item, fit_other.container)
        self.assertIs(item._fit, fit_other)
        # Misc
        fit_other.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit_other.container)

    def test_add_item_value_failure_existing_type_id(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, _eve_type_id=1, state=State.offline, spec_set=Item(1))
        item2 = Mock(_fit=None, _eve_type_id=1, state=State.offline, spec_set=Item(1))
        fit.container.add(item1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.add, item2)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], item1)
        self.assertIn(item1, fit.container)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        # Misc
        fit.container.remove(item1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_remove_item(self):
        fit = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.active, spec_set=Item(1))
        fit.container.add(item)
        # Action
        with self.fit_assertions(fit):
            fit.container.remove(item)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_remove_item_failure(self):
        fit = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.overload, spec_set=Item(1))
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(KeyError, fit.container.remove, item)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_delitem_item(self):
        fit = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.active, spec_set=Item(1))
        fit.container.add(item)
        # Action
        with self.fit_assertions(fit):
            del fit.container[1]
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_delitem_item_failure(self):
        fit = self.make_fit()
        item = Mock(_fit=None, _eve_type_id=1, state=State.active, spec_set=Item(1))
        fit.container.add(item)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(KeyError, fit.container.__delitem__, 3)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(item._fit, fit)
        # Misc
        fit.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_clear(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, _eve_type_id=1, state=State.active, spec_set=Item(1))
        item2 = Mock(_fit=None, _eve_type_id=2, state=State.online, spec_set=Item(1))
        fit.container.add(item1)
        fit.container.add(item2)
        # Action
        with self.fit_assertions(fit):
            fit.container.clear()
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(item1._fit)
        self.assertIsNone(item2._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
