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

from tests.eos_testcase import EosTestCase
from .environment import Fit


class RahTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.fit -- precreated fit with self.ch used as cache handler
    self.make_item_mock -- create eos item mock with specified
        parameters
    """

    def setUp(self):
        super().setUp()
        self.fit = Fit(self.ch)

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
