# ==============================================================================
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
# ==============================================================================


from eos.data.cachable import BaseCachable
from eos.util.repr import make_repr_str


class Attribute(BaseCachable):
    """Class which holds attribute metadata"""

    def __init__(
        self, attribute_id, max_attribute=None,
        default_value=None, high_is_good=None, stackable=None
    ):
        self.id = attribute_id

        # When value of this attribute is calculated on any item, it cannot
        # be bigger than value of attribute referenced by ID stored here
        self.max_attribute = max_attribute

        # Default value of this attribute, used when base attribute value
        # is not available on eve type during calculation process
        self.default_value = default_value

        # Boolean describing if it's good when attribute is high or not,
        # used in calculation process
        self.high_is_good = bool(high_is_good) if high_is_good is not None else None

        # Boolean which defines if attribute can be stacking penalized (False)
        # or not (True)
        self.stackable = bool(stackable) if stackable is not None else None

    # Cache-related methods
    def compress(self):
        return (
            self.id,
            self.max_attribute,
            self.default_value,
            self.high_is_good,
            self.stackable
        )

    @classmethod
    def decompress(cls, cache_handler, compressed):
        return cls(
            attribute_id=compressed[0],
            max_attribute=compressed[1],
            default_value=compressed[2],
            high_is_good=compressed[3],
            stackable=compressed[4]
        )

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
