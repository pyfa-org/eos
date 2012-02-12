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

from eos.eve.const import Type
from eos.fit.fit import Fit
from eos.fit.item.character import Character
from eos.fit.item.ship import Ship
from eos.fit.item.module import Module
from eos.fit.item.charge import Charge
from eos.fit.item.drone import Drone
from eos.fit.item.implant import Implant

class Eos:
    def __init__(self, dataHandler):
        self._dataHandler = dataHandler

    def makeFit(self):
        fit = Fit(self)
        return fit

    def makeCharacter(self):
        characterType = self._dataHandler.getType(Type.characterStatic)
        character = Character(characterType)
        return character

    def makeShip(self, typeId):
        shipType = self._dataHandler.getType(typeId)
        ship = Ship(shipType)
        return ship

    def makeModule(self, typeId):
        moduleType = self._dataHandler.getType(typeId)
        module = Module(moduleType)
        return module

    def makeCharge(self, typeId):
        chargeType = self._dataHandler.getType(typeId)
        charge = Charge(chargeType)
        return charge

    def makeDrone(self, typeId):
        droneType = self._dataHandler.getType(typeId)
        drone = Drone(droneType)
        return drone

    def makeImplant(self, typeId):
        implantType = self._dataHandler.getType(typeId)
        implant = Implant(implantType)
        return implant
