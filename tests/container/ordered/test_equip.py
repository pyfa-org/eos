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
from tests.container.environment import Fit, Item, OtherItem
from tests.container.container_testcase import ContainerTestCase


class TestContainerOrderedEquip(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIn(m.item, f.container),
            ItemRemoved: lambda f, m: self.assertIn(m.item, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = ItemList(fit, Item)
        return fit

    def test_none_to_empty(self):
        fit = self.make_fit()
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.equip, None)
        # Verification
        self.assertIs(len(fit.container), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_to_empty(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        # Action
        with self.fit_assertions(fit):
            fit.container.equip(item)
        # Verification
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], item)
        self.assertIs(item._fit, fit)
        # Cleanup
        fit.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_to_empty_type_failure(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.offline, spec_set=OtherItem(1))
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.equip, item)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(item._fit)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_to_empty_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        item = Mock(_fit=None, state=State.active, spec_set=Item(1))
        fit_other.container.equip(item)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.equip, item)
        # Verification
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], item)
        self.assertIs(item._fit, fit_other)
        # Cleanup
        fit_other.container.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_solid(self):
        # Check case when all slots of list are filled
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.active, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        item3 = Mock(_fit=None, state=State.offline, spec_set=Item(1))
        fit.container.append(item1)
        fit.container.append(item2)
        # Action
        with self.fit_assertions(fit):
            fit.container.equip(item3)
        # Verification
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[2], item3)
        self.assertIs(item3._fit, fit)
        # Cleanup
        fit.container.remove(item1)
        fit.container.remove(item2)
        fit.container.remove(item3)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_item_first_hole(self):
        # Check that leftmost empty slot is taken
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.active, spec_set=Item(1))
        item2 = Mock(_fit=None, state=State.online, spec_set=Item(1))
        item3 = Mock(_fit=None, state=State.overload, spec_set=Item(1))
        item4 = Mock(_fit=None, state=State.online, spec_set=Item(1))
        fit.container.append(item1)
        fit.container.insert(3, item2)
        fit.container.insert(6, item3)
        # Action
        with self.fit_assertions(fit):
            fit.container.equip(item4)
        # Verification
        self.assertIs(len(fit.container), 7)
        self.assertIs(fit.container[1], item4)
        self.assertIs(item4._fit, fit)
        # Cleanup
        fit.container.remove(item1)
        fit.container.remove(item2)
        fit.container.remove(item3)
        fit.container.remove(item4)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
