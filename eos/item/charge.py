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


from eos.const.eos import ModDomain
from eos.util.repr import make_repr_str
from .mixin.base import BaseItemMixin
from .mixin.state import ContainerStateMixin


class BaseCharge(ContainerStateMixin):

    def __init__(self, type_id):
        super().__init__(type_id=type_id)

    # Attribute calculation-related properties
    _modifier_domain = ModDomain.ship
    _owner_modifiable = True

    @property
    def _solsys_carrier(self):
        container = self._container
        if isinstance(container, BaseItemMixin):
            return container._solsys_carrier
        else:
            return None

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id']]
        return make_repr_str(self, spec)


class Charge(BaseCharge):
    """Represents a regular charge.

    Regular charges are manually loadable into various container items, e.g.
    various crystals, scanning probes and bombs loadable by eos user into
    modules.

    Args:
        type_id: Identifier of item type which should serve as base for this
            charge.
    """
    ...


class Autocharge(BaseCharge):
    """Represents an autocharge.

    Autocharges are spawned automatically when item type specifies it via its
    effects, eos user doesn't have to deal with them. Examples are civilian gun
    ammunition or long-range fighter bombs.
    """
    ...
