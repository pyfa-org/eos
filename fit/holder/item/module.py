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


from eos.const.eos import Location, State
from eos.fit.holder import Holder
from eos.fit.holder.attachable_functions.misc import set_state, get_tracking_speed, get_optimal_range, \
    get_falloff_range, get_cycle_time
from eos.util.volatile_cache import VolatileMixin, VolatileProperty
from .charge import Charge


class Module(Holder):
    """Ship's module from any slot."""

    __slots__ = ('__charge',)

    def __init__(self, type_id, state=State.offline, charge=None):
        Holder.__init__(self, type_id, state)
        self.__charge = None
        self.charge = charge

    @property
    def _location(self):
        return Location.ship

    @property
    def _other(self):
        """Purely service property, used in fit link tracker registry"""
        return self.charge

    tracking_speed = property(get_tracking_speed)
    optimal_range = property(get_optimal_range)
    falloff_range = property(get_falloff_range)
    cycle_time = property(get_cycle_time)

    @Holder.state.setter
    def state(self, new_state):
        set_state(self, new_state)

    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, new_charge):
        if new_charge is not None:
            # Check what's being assigned
            if not isinstance(new_charge, Charge):
                msg = 'only {} and None are accepted, not {}'.format(
                    Charge, type(new_charge))
                raise TypeError(msg)
            # Also check if it is attached to other fit already
            # or not. We can't rely on fit._add_holder to do it,
            # because charge can be assigned when module is detached
            # from fit, which breaks consistency - both holders
            # need to be assigned to the same fit
            if new_charge._fit is not None:
                raise ValueError(new_charge)
        old_charge = self.charge
        if old_charge is not None:
            if self._fit is not None:
                self._fit._remove_holder(old_charge)
            old_charge.container = None
        self.__charge = new_charge
        if new_charge is not None:
            new_charge.container = self
            if self._fit is not None:
                self._fit._add_holder(new_charge)
