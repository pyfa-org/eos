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


from itertools import chain
from unittest.mock import Mock

from eos.fit.stats import StatService
from eos.fit.messages import ItemAdded, ItemRemoved, EnableServices
from tests.eos_testcase import EosTestCase


class StatTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.ss -- stats service instance for tests
    self.make_item_mock -- create eos item mock with specified
        parameters
    self.set_ship -- set ship to fit which uses stats service
    self.set_character -- set character to fit which uses stats
        service
    self.add_item -- add item to stats service
    self.remove_item -- remove item from stats service
    self.assert_stat_buffers_empty -- checks if stats service
        buffers are clear
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
        self.ss = StatService(self.fit)
        self.ss._notify(EnableServices(items=()))

    def make_item_mock(self, item_class, eve_type, state=None, strict_spec=True):
        item = item_class(eve_type.id)
        state = state if state is not None else item.state
        kwargs = {
            '_eve_type_id': eve_type.id,
            '_eve_type': eve_type,
            'state': state,
            '_parent_modifier_domain': item._parent_modifier_domain,
            'spec_set' if strict_spec is True else 'spec': item
        }
        return Mock(**kwargs)

    def set_ship(self, item):
        self.fit.ship = item

    def set_character(self, item):
        self.fit.character = item

    def add_item(self, item):
        self.ss._notify(ItemAdded(item))

    def remove_item(self, item):
        self.ss._notify(ItemRemoved(item))

    def assert_stat_buffers_empty(self):
        entry_num = 0
        # Get all registers used by service and cycle through them
        for register in chain(
                self.ss._StatService__regs_stateless,
                *self.ss._StatService__regs_stateful.values()
        ):
            entry_num += self._get_object_buffer_entry_amount(register)
        # Raise error if we found any data in any register
        if entry_num > 0:
            plu = 'y' if entry_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(entry_num, plu)
            self.fail(msg=msg)
