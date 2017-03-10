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


class TestContainerOrderedAppend(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIn(m.item, f.container),
            ItemRemoved: lambda f, m: self.assertIn(m.item, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = ItemList(fit, Item)
        return fit

    def custom_membership_check(self, fit, item):
        self.assertIn(item, fit.container)

    def test_none(self):
        # Action
        self.assertRaises(TypeError, fit.container.append, None)
        # Verification
        self.assertIs(len(fit.container), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item(self):
        item1 = Item(self.ch.type().id)
        item2 = Item(self.ch.type().id)
        # Action
        fit.container.append(item1)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        # Action
        fit.container.append(item2)
        # Verification
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], item1)
        self.assertIs(fit.container[1], item2)
        self.assertIs(item1._fit, fit)
        self.assertIs(item2._fit, fit)
        # Cleanup
        fit.container.remove(item1)
        fit.container.remove(item2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_type_failure(self):
        item = OtherItem(self.ch.type().id)
        # Action
        self.assertRaises(TypeError, fit.container.append, item)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_value_failure(self):
        fit_other = self.make_fit()
        item = Item(self.ch.type().id)
        fit_other.container.append(item)
        # Action
        self.assertRaises(ValueError, fit.container.append, item)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], item)
        self.assertIs(item._fit, fit_other)
        # Cleanup
        fit_other.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit_other.container)
