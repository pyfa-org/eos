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

from eos.fit.messages import HolderAdded, HolderRemoved
from tests.eos_testcase import EosTestCase
from .environment import Fit


class ContainerTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assert_fit_buffers_empty -- checks if fit has any
    holders assigned to it.
    self.make_fit -- create fit, which keeps track of list
    of holders which were added via messages, and provides
    ability for tests to do some verifications when holder
    is being added/removed via custom_membership_check
    method.
    """

    def assert_fit_buffers_empty(self, fit):
        holder_num = 0
        # Fit here is simple stub - check ship and
        # test holder storage
        if fit.ship is not None:
            holder_num += 1
        holder_num += len(fit.test_holders)
        if holder_num > 0:
            plu = 'y' if holder_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(holder_num, plu)
            self.fail(msg=msg)

    def make_fit(self):
        fit = Fit()
        self.__add_membership_checks(fit)
        return fit

    def __add_membership_checks(self, fit):
        fit.test_holders = set()

        def handle_add_holder(message):
            self.assertNotIn(message.holder, fit.test_holders)
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, message.holder)
            fit.test_holders.add(message.holder)

        def handle_remove_holder(message):
            self.assertIn(message.holder, fit.test_holders)
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, message.holder)
            fit.test_holders.remove(message.holder)

        handler_map = {
            HolderAdded: handle_add_holder,
            HolderRemoved: handle_remove_holder
        }

        def handle_message(message):
            handler_map[type(message)](message)

        fit._subscribe = Mock()
        fit._unsubscribe = Mock()
        fit._publish = Mock()
        fit._publish.side_effect = handle_message

        return fit
