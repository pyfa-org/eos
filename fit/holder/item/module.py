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
from eos.fit.holder.container import HolderDescriptorOnHolder
from eos.fit.holder.mixin.misc import SpecialAttribMixin
from eos.fit.holder.mixin.state import MutableStateMixin
from .charge import Charge


class Module(Holder,
             MutableStateMixin,
             SpecialAttribMixin):

    def __init__(self, type_id, state=State.offline, charge=None, **kwargs):
        super().__init__(type_id=type_id, state=state, **kwargs)
        self.charge = charge

    @property
    def _location(self):
        return Location.ship

    charge = HolderDescriptorOnHolder('_charge', 'container', Charge)

    @property
    def _other(self):
        """Purely service property, used in fit link tracker registry"""
        return self.charge


class ModuleHigh(Module):
    """
    Ship's module from high slot.

    This class has following methods designed cooperatively:
    __init__
    """
    pass


class ModuleMed(Module):
    """
    Ship's module from medium slot.

    This class has following methods designed cooperatively:
    __init__
    """
    pass


class ModuleLow(Module):
    """
    Ship's module from low slot.

    This class has following methods designed cooperatively:
    __init__
    """
    pass
