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

from eos import const
from eos.fit import Fit, Character, Ship, Module, Charge

class Eos:
    def __init__(self, dataHandler):
        self.__dataHandler = dataHandler

    def makeFit(self):
        fit = Fit()
        return fit

    def makeCharacter(self):
        characterType = self.__dataHandler.getType(const.typeCharacterAmarr)
        character = Character(characterType)
        return character

    def makeShip(self, typeId):
        shipType = self.__dataHandler.getType(typeId)
        ship = Ship(shipType)
        return ship

    def makeModule(self, typeId):
        moduleType = self.__dataHandler.getType(typeId)
        module = Module(moduleType)
        return module

    def makeCharge(self, typeId):
        chargeType = self.__dataHandler.getType(typeId)
        charge = Charge(chargeType)
        return charge
