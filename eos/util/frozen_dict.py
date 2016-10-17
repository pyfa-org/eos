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


"""
Recipe taken from http://code.activestate.com/recipes/414283-frozen-dictionaries/
"""


from .cached_property import CachedProperty


class FrozenDict(dict):

    def __new__(cls, *args):
        new = dict.__new__(cls)
        dict.__init__(new, *args)
        return new

    def _blocked_attribute(self, *args, **kwargs):
        raise TypeError('frozendict cannot be modified')

    # Prohibit use of methods which modify dictionary
    __delitem__ = __setitem__ = clear = pop = popitem = setdefault = update = _blocked_attribute

    @CachedProperty
    def _hash(self):
        return hash(frozenset(self.items()))

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return 'frozendict({})'.format(dict.__repr__(self))
