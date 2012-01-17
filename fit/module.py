#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.calc.info.info import InfoLocation
from eos.calc.mutableAttributeHolder import MutableAttributeHolder


class Module(MutableAttributeHolder):
    """Represents single module"""

    def __init__(self, invType):
        super().__init__(invType)
        self.__charge = None

    def _getLocation(self):
        return InfoLocation.ship

    def _getOther(self):
        """Purely service property, used in fit registry"""
        return self.charge

    @property
    def charge(self):
        """Get charge holder of module"""
        return self.__charge

    @charge.setter
    def charge(self, newCharge):
        """Set charge holder of module"""
        # Way of processing it is exactly the same as with fit's ship or
        # character: unset old charge, and set new one, making sure that all
        # modifiers are reapplied by passing special location keyword argument
        oldCharge = self.charge
        if oldCharge is not None:
            self.fit._removeHolder(oldCharge, disableDirect=InfoLocation.other)
            self.__charge = None
            oldCharge.container = None
        if newCharge is not None:
            newCharge.container = self
            self.__charge = newCharge
            self.fit._addHolder(newCharge, enableDirect=InfoLocation.other)

    def trackingSpeed(self):
        tsAttrId = self.invType._trackingSpeedAttributeId
        if tsAttrId is not None:
            tracking = self.attributes[tsAttrId]
        else:
            tracking = None
        return tracking

    def optimalRange(self):
        orAttrId = self.invType._rangeAttributeId
        if orAttrId is not None:
            optimal = self.attributes[orAttrId]
        else:
            optimal = None
        return optimal

    def falloffRange(self):
        frAttrId = self.invType._falloffAttributeId
        if frAttrId is not None:
            falloff = self.attributes[frAttrId]
        else:
            falloff = None
        return falloff
