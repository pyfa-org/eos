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


from eos.fit.holder.item import Charge


class ChargeableMixin:

    def __init__(self, charge, **kwargs):
        self.__charge = None
        super().__init__(**kwargs)
        # Assign charge properly only after initialization by
        # next classes is complete, because setting it relies on
        # _fit attribute which may be not initialized yet
        self.charge = charge

    @property
    def _other(self):
        """Purely service property, used in fit link tracker registry"""
        return self.charge

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
        fit = self._fit
        if old_charge is not None:
            if fit is not None:
                fit._clear_volatile_data()
                fit._remove_holder(old_charge)
            old_charge.container = None
        self.__charge = new_charge
        if new_charge is not None:
            new_charge.container = self
            if fit is not None:
                fit._add_holder(new_charge)
                fit._clear_volatile_data()
