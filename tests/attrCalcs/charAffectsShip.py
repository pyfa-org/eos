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

from unittest import TestCase

from eos import const
from eos.data import Attribute
from eos.data import InvType
from eos.data import Effect
from eos.data.effect import EffectInfo
from eos.fit import Fit, Ship, Character

class TestCharAffectsShip(TestCase):

    def testAttrCalc(self):
        fit = Fit()

        attrShip = Attribute(1, 1, 0)
        ship1 = Ship(InvType(1, None, None, {}, {attrShip.id: 100}, {attrShip.id: attrShip}))
        ship2 = Ship(InvType(2, None, None, {}, {attrShip.id: 20}, {attrShip.id: attrShip}))


        attrChar = Attribute(2, 1, 0)
        info = EffectInfo()
        info.type = const.infoDuration
        info.location = const.locShip
        info.operator = const.optrPostPercent
        info.targetAttribute = attrShip.id
        info.sourceType = const.srcAttr
        info.sourceValue = attrChar.id
        modEffect = Effect(1, None, None, 0, 0)
        modEffect._Effect__infos = {info}
        char = Character(InvType(3, None, None, {modEffect}, {attrChar.id: 40}, {attrChar.id: attrChar}))
        fit.character = char

        fit.ship = ship1
        expVal = 140
        self.assertAlmostEqual(ship1.attributes[attrShip.id], expVal)

        # Then, check if after removal of modifier it's disabled properly,
        # to become enabled once again for other charge
        fit.ship = ship2
        expVal = 28
        self.assertAlmostEqual(ship2.attributes[attrShip.id], expVal)
