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
from eos.fit.holder.item import Ship
from eos.fit.messages import HolderAdded, HolderRemoved
from tests.holder_container.environment import Fit, OtherHolder
from tests.holder_container.container_testcase import ContainerTestCase


class TestDirectHolderShip(ContainerTestCase):

    def make_fit(self):
        assertions = {
            HolderAdded: lambda f, m: self.assertIs(f.ship, m.holder),
            HolderRemoved: lambda f, m: self.assertIs(f.ship, m.holder)
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

    def test_none_to_holder(self):
        fit = self.make_fit()
        fit.ship = None
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        # Action
        with self.fit_assertions(fit):
            fit.ship = holder
        # Checks
        self.assertIs(fit.ship, holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ship = None
        self.assertIsNone(fit.ship)
        self.assert_fit_buffers_empty(fit)

    def test_none_to_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=OtherHolder(1))
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.__setattr__, 'ship', holder)
        # Checks
        self.assertIsNone(fit.ship)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_none_to_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit_other.ship = holder
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.__setattr__, 'ship', holder)
        # Checks
        self.assertIsNone(fit.ship)
        self.assertIs(fit_other.ship, holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_holder_to_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = holder1
        # Action
        with self.fit_assertions(fit):
            fit.ship = holder2
        # Checks
        self.assertIs(fit.ship, holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_holder_to_holder_type_failure(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=OtherHolder(1))
        fit.ship = holder1
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.__setattr__, 'ship', holder2)
        # Checks
        self.assertIs(fit.ship, holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_holder_to_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Ship(1))
        fit.ship = holder1
        fit_other.ship = holder2
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.__setattr__, 'ship', holder2)
        # Checks
        self.assertIs(fit.ship, holder1)
        self.assertIs(fit_other.ship, holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit_other)
        # Misc
        fit.ship = None
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_holder_to_none(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = holder
        # Action
        with self.fit_assertions(fit):
            fit.ship = None
        # Checks
        self.assertIsNone(fit.ship)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
