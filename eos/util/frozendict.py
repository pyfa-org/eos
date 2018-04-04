# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


"""
Initial version taken from
http://code.activestate.com/recipes/414283-frozen-dictionaries/
with further modifications by me.
"""


class frozendict(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__hash = None

    def __blocked_attr(self, *args, **kwargs):
        raise TypeError('frozendict cannot be modified')

    # Prohibit use of methods which modify dictionary
    __delitem__ = __setitem__ = clear = pop = popitem = setdefault = update = (
        __blocked_attr)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash(frozenset(self.items()))
        return self.__hash

    def __repr__(self):
        return 'frozendict({})'.format(dict.__repr__(self))
