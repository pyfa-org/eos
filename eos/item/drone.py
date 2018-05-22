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


from eos.const.eos import State
from eos.util.repr import make_repr_str
from .mixin.effect_stats import EffectStatsMixin
from .mixin.solar_system import SolarSystemItemMixin
from .mixin.state import MutableStateMixin
from .mixin.tanking import BufferTankingMixin
from .mixin.targetable import SingleTargetableMixin


class Drone(
        MutableStateMixin, BufferTankingMixin,
        EffectStatsMixin, SolarSystemItemMixin,
        SingleTargetableMixin):
    """Represents a single drone.

    Eos doesn't unify multiple drones into stacks, it should be done in services
    built on top of it.

    Args:
        type_id: Identifier of item type which should serve as base for this
            drone.
        state (optional): Initial state this drone takes, default is offline
            (drone in drone bay).
    """

    def __init__(self, type_id, state=State.offline):
        super().__init__(type_id=type_id, state=state)

    # Attribute calculation-related properties
    _modifier_domain = None
    _owner_modifiable = True

    @property
    def _solsys_carrier(self):
        return self

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id'], 'state']
        return make_repr_str(self, spec)
