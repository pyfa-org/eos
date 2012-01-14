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
from eos.fit import Fit, Ship, Module

class TestShipMod(TestCase):
    """This is just experimental test case to see how they should be written"""

    def testJust(self):
        shipTgtAttr = Attribute(1, 1, 0)
        ship = Ship(InvType(1, 0, 0, {}, {1: 100}, {1: shipTgtAttr}))
        modSrcAttr = Attribute(2, 1, 0)
        modEffect = Effect(1, 0, 0, 0, 0)
        info = EffectInfo()
        info.type = const.infoDuration
        info.location = const.locShip
        info.operator = const.optrPostPercent
        info.targetAttribute = 1
        info.sourceType = const.srcAttr
        info.sourceValue = 2
        modEffect.infoStatus = const.effectInfoOkFull
        modEffect._Effect__infos = {info}
        module = Module(InvType(2, 0, 0, {modEffect}, {2: 20}, {2: modSrcAttr}))
        fit = Fit()
        fit.ship = ship
        fit.modules.append(module)
        expVal = 120
        self.assertAlmostEqual(ship.attributes[1], expVal)


