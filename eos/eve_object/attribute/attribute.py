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
    """Represents eve attribute with all its metadata.

    Attributes:
        id: Identifier of the attribute.
        max_attribute: When specified, value of current attribute on an item
            cannot exceed value of this attribute on the very same item.
        default_value: Base value for attribute. Used when value of the
            attribute with this ID is not specified on item.
        high_is_good: Boolean flag which defines if it's good when attribute has
            high value or not. Used in calculation process.
        stackable: Boolean flag which defines if attribute can be stacking
            penalized (False) or not (True).
    """

    def __init__(
        self,
        attribute_id,
        max_attribute=None,
        default_value=None,
        high_is_good=True,
        stackable=True
    ):
        self.id = attribute_id
        self.max_attribute = max_attribute
        self.default_value = default_value
        self.high_is_good = bool(high_is_good)
        self.stackable = bool(stackable)

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
