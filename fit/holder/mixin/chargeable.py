#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.const.eve import Attribute
from eos.fit.holder.container import HolderDescriptorOnHolder
from eos.fit.holder.item import Charge
from eos.util.override import OverrideDescriptor
from eos.util.volatile_cache import CooperativeVolatileMixin, VolatileProperty
from .holder import HolderBase


class ChargeableMixin(HolderBase, CooperativeVolatileMixin):
    """
    Mixin intended to use with holders which can have charge loaded
    into them.

    Required arguments:
    charge -- charge to be loaded into holder

    Cooperative methods:
    __init__
    """

    def __init__(self, charge, **kwargs):
        super().__init__(**kwargs)
        self.charge = charge

    charge = HolderDescriptorOnHolder('_charge', 'container', Charge)

    @VolatileProperty
    def charge_max_quantity(self):
        """
        Return max quantity of loadable charges as integer, based
        on the container capacity and charge volume. If any of these
        is not defined, or no charge is found in holder, None is returned.
        """
        if self.charge is None:
            return None
        container_capacity = self.attributes.get(Attribute.capacity)
        charge_volume = self.charge.attributes.get(Attribute.volume)
        if container_capacity is None or charge_volume is None:
            return None
        # Run rounding to negate float representation inaccuracies
        # (e.g. to have 2.3 / 0.1 at 23, not 22)
        charges = int(round(container_capacity / charge_volume, 9))
        return charges

    charge_quantity = OverrideDescriptor('charge_max_quantity')
