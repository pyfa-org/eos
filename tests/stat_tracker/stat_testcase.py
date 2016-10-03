# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
from eos.fit.stat_tracker import StatTracker
from tests.eos_testcase import EosTestCase


class StatTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.rt -- restriction tracker instance for tests
    self.set_ship -- set ship to fit which uses self.rt
    self.set_character -- set character to fit whic uses
    self.rt
    self.track_holder -- add holder to restriction tracker
    self.untrack_holder -- remove holder from restriction
    tracker
    self.get_restriction_error -- get restriction error for
    passed holder of passed restriction type. If no error
    occurred, return None
    self.assert_restriction_buffers_empty -- checks if
    restriction tracker buffers are clear
    """

    def setUp(self):
        super().setUp()
        self.fit = Mock()
        self.fit.ship = None
        self.fit.character = None
        self.fit.modules.high = []
        self.fit.modules.med = []
        self.fit.modules.low = []
        self.fit.rigs = set()
        self.fit.subsystems = set()
        self.fit.drones = set()
        self.st = StatTracker(self.fit)

    def set_ship(self, holder):
        self.fit.ship = holder

    def set_character(self, holder):
        self.fit.character = holder

    def track_holder(self, holder):
        self.st._enable_states(holder, set(filter(lambda s: s <= holder.state, State)))

    def untrack_holder(self, holder):
        self.st._disable_states(holder, set(filter(lambda s: s <= holder.state, State)))

    def assert_stat_buffers_empty(self):
        entry_num = 0
        # Get dictionary-container with all registers used by tracker,
        # and cycle through all of them
        tracker_container = self.st._StatTracker__registers
        for register_group in tracker_container.values():
            for register in register_group:
                entry_num += self._get_object_buffer_entry_amount(register)
        # Raise error if we found any data in any register
        if entry_num > 0:
            plu = 'y' if entry_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(entry_num, plu)
            self.fail(msg=msg)
