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
from eos.const.eve import AttrId
from eos.util.repr import make_repr_str
from .mixin.chargeable import ChargeableMixin
from .mixin.dmg_dealer import DmgDealerMixin
from .mixin.defeff_proxy import DefaultEffectProxyMixin
from .mixin.state import MutableStateMixin


class Module(
        MutableStateMixin, ChargeableMixin, DmgDealerMixin,
        DefaultEffectProxyMixin):
    def __init__(self, type_id, state=State.offline, charge=None):
        super().__init__(type_id=type_id, state=state, charge=charge)

    @property
    def reactivation_delay(self):
        delay_ms = self.attrs.get(AttrId.module_reactivation_delay)
        if delay_ms is None:
            return None
        return delay_ms / 1000

    # Attribute calculation-related properties
    _modifier_domain = ModDomain.ship
    _owner_modifiable = False

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id'], 'state', 'charge']
        return make_repr_str(self, spec)


class ModuleHigh(Module):
    """Represents a high-slot module.

    Args:
        type_id: Identifier of item type which should serve as base for this
            module.
        state (optional): Initial state this module takes, default is offline.
        charge (optional): Charge object to load into module, default is None.
    """
    ...


class ModuleMed(Module):
    """Represents a med-slot module.

    Args:
        type_id: Identifier of item type which should serve as base for this
            module.
        state (optional): Initial state this module takes, default is offline.
        charge (optional): Charge object to load into module, default is None.
    """
    ...


class ModuleLow(Module):
    """Represents a low-slot module.

    Args:
        type_id: Identifier of item type which should serve as base for this
            module.
        state (optional): Initial state this module takes, default is offline.
        charge (optional): Charge object to load into module, default is None.
    """
    ...
