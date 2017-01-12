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


from itertools import chain
from unittest.mock import Mock

from eos.const.eos import Restriction, State
from eos.fit.messages import HolderAdded, HolderRemoved, EnableServices
from eos.fit.restrictions import RestrictionService, ValidationError
from tests.eos_testcase import EosTestCase


class RestrictionTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.rs -- restriction service instance for tests
    self.set_ship -- set ship to fit which uses restriction
    service
    self.set_character -- set character to fit which uses
    restriction service
    self.add_holder -- add holder to restriction service
    self.remove_holder -- remove holder from restriction
    service
    self.get_restriction_error -- get restriction error for
    passed holder of passed restriction type. If no error
    occurred, return None
    self.assert_restriction_buffers_empty -- checks if
    restriction service buffers are clear
    """

    def setUp(self):
        super().setUp()
        self.fit = Mock()
        self.fit.ship = None
        self.fit.character = None
        self.fit.skills = {}
        self.fit.modules.high = []
        self.fit.modules.med = []
        self.fit.modules.low = []
        self.fit.rigs = set()
        self.fit.subsystems = set()
        self.fit.drones = set()
        self.rs = RestrictionService(self.fit)
        self.rs._notify(EnableServices(holders=()))

    def set_ship(self, holder):
        self.fit.ship = holder

    def add_holder(self, holder):
        self.rs._notify(HolderAdded(holder))

    def remove_holder(self, holder):
        self.rs._notify(HolderRemoved(holder))

    def get_restriction_error(self, holder, restriction):
        skip_checks = set(Restriction).difference((restriction,))
        try:
            self.rs.validate(skip_checks)
        except ValidationError as e:
            error_data = e.args[0]
            if holder not in error_data:
                return None
            holder_error = error_data[holder]
            if restriction not in holder_error:
                return None
            return holder_error[restriction]
        else:
            return None

    def assert_restriction_buffers_empty(self):
        entry_num = 0
        # Get all registers used by service and cycle through them
        for register in chain(
                self.rs._RestrictionService__regs_stateless,
                *self.rs._RestrictionService__regs_stateful.values()
        ):
            entry_num += self._get_object_buffer_entry_amount(register)
        # Raise error if we found any data in any register
        if entry_num > 0:
            plu = 'y' if entry_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(entry_num, plu)
            self.fail(msg=msg)
