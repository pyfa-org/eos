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


from eos.const.eos import State
from eos.util.repr import make_repr_str
from .mixin.damage_dealer import DamageDealerMixin
from .mixin.defeff_proxy import DefaultEffectProxyMixin
from .mixin.state import MutableStateMixin
from .mixin.tanking import BufferTankingMixin


class FighterSquad(
    MutableStateMixin, DamageDealerMixin,
    BufferTankingMixin, DefaultEffectProxyMixin
):
    """Represents a fighter squad.

    Unlike drones, fighter squad is single entity.

    Args:
        type_id: Identifier of eve type which should serve as base for this
            fighter squad.
        state (optional): Initial state fighter squad takes, default is offline
            (squad is in fighter tube).
    """

    def __init__(self, type_id, state=State.offline):
        super().__init__(type_id=type_id, state=state)

    # Attribute calculation-related properties
    _parent_modifier_domain = None
    _owner_modifiable = True

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_eve_type_id'], 'state']
        return make_repr_str(self, spec)
