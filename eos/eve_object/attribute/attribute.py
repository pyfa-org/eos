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


from eos.util.repr import make_repr_str


class Attribute:
    """Represents eve attribute with all its metadata.

    Attributes:
        id: Identifier of the attribute.
        max_attr_id: When specified, value of current attribute on an item
            cannot exceed value of attribute with this ID on the item.
        default_value: Base value for attribute. Used when value of the
            attribute with this ID is not specified on an item.
        high_is_good: Boolean flag which defines if it's good when attribute has
            high value or not. Used in calculation process.
        stackable: Boolean flag which defines if attribute can be stacking
            penalized (False) or not (True).
    """

    def __init__(
            self, attr_id, max_attr_id=None, default_value=None,
            high_is_good=True, stackable=True):
        self.id = attr_id
        self.max_attr_id = max_attr_id
        self.default_value = default_value
        self.high_is_good = bool(high_is_good)
        self.stackable = bool(stackable)

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
