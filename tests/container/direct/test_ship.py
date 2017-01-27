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
from eos.fit.item import Ship
from eos.fit.messages import ItemAdded, ItemRemoved
from tests.container.environment import Fit, OtherItem
from tests.container.container_testcase import ContainerTestCase


class TestDirectItemShip(ContainerTestCase):

    def make_fit(self):
        assertions = {
            ItemAdded: lambda f, m: self.assertIs(f.ship, m.item),
            ItemRemoved: lambda f, m: self.assertIs(f.ship, m.item)
        }
        fit = Fit(self, message_assertions=assertions)
        return fit

    def test_none_to_none(self):
        fit = self.make_fit()
        # Action
        with self.fit_assertions(fit):
            fit.ship = None
        # Checks
        self.assertIsNone(fit.ship)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_none_to_item(self):
        fit = self.make_fit()
        fit.ship = None
        item = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        # Action
        with self.fit_assertions(fit):
            fit.ship = item
        # Checks
        self.assertIs(fit.ship, item)
        self.assertIs(item._fit, fit)
        # Misc
        fit.ship = None
        self.assertIsNone(fit.ship)
        self.assert_fit_buffers_empty(fit)

    def test_none_to_item_type_failure(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.active, spec_set=OtherItem(1))
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.__setattr__, 'ship', item)
        # Checks
        self.assertIsNone(fit.ship)
        self.assertIsNone(item._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_none_to_item_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        item = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit_other.ship = item
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.__setattr__, 'ship', item)
        # Checks
        self.assertIsNone(fit.ship)
        self.assertIs(fit_other.ship, item)
        self.assertIs(item._fit, fit_other)
        # Misc
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_item_to_item(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.offline, spec_set=Ship(1))
        item2 = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = item1
        # Action
        with self.fit_assertions(fit):
            fit.ship = item2
        # Checks
        self.assertIs(fit.ship, item2)
        self.assertIsNone(item1._fit)
        self.assertIs(item2._fit, fit)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_item_to_item_type_failure(self):
        fit = self.make_fit()
        item1 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        item2 = Mock(_fit=None, state=State.overload, spec_set=OtherItem(1))
        fit.ship = item1
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.__setattr__, 'ship', item2)
        # Checks
        self.assertIs(fit.ship, item1)
        self.assertIs(item1._fit, fit)
        self.assertIsNone(item2._fit)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_item_to_item_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        item1 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        item2 = Mock(_fit=None, state=State.overload, spec_set=Ship(1))
        fit.ship = item1
        fit_other.ship = item2
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.__setattr__, 'ship', item2)
        # Checks
        self.assertIs(fit.ship, item1)
        self.assertIs(fit_other.ship, item2)
        self.assertIs(item1._fit, fit)
        self.assertIs(item2._fit, fit_other)
        # Misc
        fit.ship = None
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_item_to_none(self):
        fit = self.make_fit()
        item = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = item
        # Action
        with self.fit_assertions(fit):
            fit.ship = None
        # Checks
        self.assertIsNone(fit.ship)
        self.assertIsNone(item._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
