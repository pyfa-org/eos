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


from eos.const.eos import ModDomain
from eos.const.eos import State
from eos.const.eve import AttrId
from eos.fit.item import Charge
from eos.fit.item_container import ItemDescriptor
from eos.util.float import float_to_int
from eos.util.repr import make_repr_str
from .mixin.effect_stats import EffectStatsMixin
from .mixin.state import MutableStateMixin


class Module(MutableStateMixin, EffectStatsMixin):

    def __init__(self, type_id, state=State.offline, charge=None):
        super().__init__(type_id=type_id, state=state)
        self.charge = charge

    # Charge-specific properties
    charge = ItemDescriptor('_charge', Charge)

    def _child_item_iter(self, **kwargs):
        charge = self.charge
        if charge is not None:
            yield charge
        # Try next in MRO
        try:
            child_item_iter = super()._child_item_iter
        except AttributeError:
            pass
        else:
            for item in child_item_iter(**kwargs):
                yield item

    @property
    def charge_quantity(self):
        """Max quantity of loadable charges.

        It depends on capacity of this item and volume of charge.

        Returns:
            Quantity of loadable charges as integer. If any of necessary
            attribute values is not defined, or no charge is found in item, None
            is returned.
        """
        if self.charge is None:
            return None
        container_capacity = self.attrs.get(AttrId.capacity)
        charge_volume = self.charge.attrs.get(AttrId.volume)
        if container_capacity is None or charge_volume is None:
            return None
        charges = float_to_int(container_capacity / charge_volume)
        return charges

    @property
    def cycles_until_reload(self):
        """Quantity of cycles item can run until charges are depleted.

        Relays calculation to effect, because final value depends on effect
        type.
        """
        item_type = self._type
        if item_type is None:
            return None
        try:
            getter = item_type.default_effect.get_cycles_until_reload
        except AttributeError:
            return None
        else:
            return getter(self)

    @property
    def reload_time(self):
        """Returns item reload time in seconds."""
        time_ms = self.attrs.get(AttrId.reload_time)
        try:
            return time_ms / 1000
        except TypeError:
            return time_ms

    # Item-specific properties
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
