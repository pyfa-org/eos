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


from eos.const.eos import ModDomain, State
from eos.util.repr import make_repr_str
from .mixin.state import ImmutableStateMixin


class Stance(ImmutableStateMixin):
    """Represents a stance.

    Stance is internal name for tech 3 destroyer tactical modes.

    Args:
        type_id: Identifier of item type which should serve as base for this
            stance.
    """

    def __init__(self, type_id):
        super().__init__(type_id=type_id, state=State.offline)

    # Attribute calculation-related properties
    _parent_modifier_domain = ModDomain.ship
    _owner_modifiable = False

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id']]
        return make_repr_str(self, spec)
