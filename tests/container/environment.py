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
from eos.fit.container import HolderDescriptorOnFit
from eos.fit.item import Ship
from eos.fit.item.mixin.state import MutableStateMixin
from eos.fit.messages import HolderAdded, HolderRemoved


class Holder(MutableStateMixin):

    def __init__(self, type_id, state=State.offline, **kwargs):
        super().__init__(type_id=type_id, state=state, **kwargs)

    _domain = None
    _owner_modifiable = None


class OtherHolder(MutableStateMixin):

    def __init__(self, type_id, state=State.offline, **kwargs):
        super().__init__(type_id=type_id, state=state, **kwargs)

    _domain = None
    _owner_modifiable = None


class Fit:

    def __init__(self, test, message_assertions=None):
        self.test = test
        self._message_assertions = message_assertions
        self.assertions_enabled = False
        self.test_holders = set()
        self._subscribe = Mock()
        self._unsubscribe = Mock()

    ship = HolderDescriptorOnFit('_ship', Ship)

    def handle_add_holder(self, message):
        self.test.assertNotIn(message.holder, self.test_holders)
        self.test_holders.add(message.holder)

    def handle_remove_holder(self, message):
        self.test.assertIn(message.holder, self.test_holders)
        self.test_holders.remove(message.holder)

    handler_map = {
        HolderAdded: handle_add_holder,
        HolderRemoved: handle_remove_holder
    }

    def _publish(self, message):
        if self._message_assertions is not None and self.assertions_enabled is True:
            try:
                assertion = self._message_assertions[type(message)]
            except KeyError:
                pass
            else:
                assertion(self, message)
        self.handler_map[type(message)](self, message)


class FitAssertion:

    def __init__(self, fit):
        self.fit = fit

    def __enter__(self):
        self.fit.assertions_enabled = True

    def __exit__(self, *args):
        self.fit.assertions_enabled = False
