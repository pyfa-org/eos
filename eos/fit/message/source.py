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


from eos.util.repr import make_repr_str
from .base import BaseMessage
from .item import ItemAdded, ItemRemoved


class SourceChanged(BaseMessage):

    def __init__(self, old, new, items):
        self.old = old
        self.new = new
        self.items = items

    def expand(self):
        expanded = []
        # If old source wasn't None, ask to remove all items from everywhere but fit
        if self.old is not None:
            for item in self.items:
                expanded.extend(ItemRemoved(item, source_switch=True).expand())
        # Ask every source-dependent to update source
        expanded.append(RefreshSource())
        # If new source isn't None, add new items back
        if self.new is not None:
            for item in self.items:
                expanded.extend(ItemAdded(item, source_switch=True).expand())
        return expanded

    def __repr__(self):
        spec = ['old', 'new', 'items']
        return make_repr_str(self, spec)


class RefreshSource(BaseMessage)

    def __repr__(self):
        return make_repr_str(self, ())
