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
from eos.fit.holder.container import HolderDescriptorOnHolder


class ChargeContainerMixin:

    def __init__(self, charge, **kwargs):
        super().__init__(**kwargs)
        # Assign charge properly only after initialization by
        # next classes is complete, because setting it relies on
        # _fit attribute which may be not initialized by the moment
        # our current init is called
        self.charge = charge

    charge = HolderDescriptorOnHolder('_charge', 'container', Charge)

    @property
    def _other(self):
        """Purely service property, used in fit link tracker registry"""
        return self.charge
