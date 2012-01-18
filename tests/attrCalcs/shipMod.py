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

from eos.eve.attribute import Attribute
from eos.eve.invType import InvType
from eos.eve.effect import Effect
from eos.calc.info.info import Info, InfoRunTime, InfoLocation, InfoOperator, InfoSourceType
from eos.fit.fit import Fit
from eos.fit.ship import Ship
from eos.fit.module import Module


class TestShipMod(TestCase):
    """This is just experimental test case to see how they should be written"""

    def testJust(self):
        def attrMetaGetter(attrId):
            attrs = {1: Attribute(1, highIsGood=1, stackable=1),
                     2: Attribute(2, highIsGood=1, stackable=1)}
            return attrs[attrId]

        shipTgtAttr = attrMetaGetter(1)
        ship = Ship(InvType(1, attributes={1: 100}))
        modSrcAttr = attrMetaGetter(2)
        modEffect = Effect(1)
        info = Info()
        info.runTime = InfoRunTime.duration
        info.location = InfoLocation.ship
        info.operator = InfoOperator.postPercent
        info.targetAttribute = shipTgtAttr.id
        info.sourceType = InfoSourceType.attribute
        info.sourceValue = modSrcAttr.id
        modEffect._Effect__infos = {info}
        module = Module(InvType(2, effects={modEffect}, attributes={2: 20}))
        fit = Fit(attrMetaGetter)
        fit.ship = ship
        fit.modules.append(module)
        expVal = 120
        self.assertAlmostEqual(ship.attributes[1], expVal)


