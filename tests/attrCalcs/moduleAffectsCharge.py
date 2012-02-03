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
from eos.eve.type import Type
from eos.eve.effect import Effect
from eos.fit.calc.info.info import Info
from eos.const import State, Context, RunTime, Location, Operator, SourceType
from eos.fit.fit import Fit
from eos.fit.items.ship import Ship
from eos.fit.items.module import Module
from eos.fit.items.charge import Charge


class TestModuleAffectsCharge(TestCase):

    def testAttrCalc(self):

        def attrMetaGetter(attrId):
            attrs = {1: Attribute(1, highIsGood=1, stackable=1),
                     2: Attribute(2, highIsGood=1, stackable=1)}
            return attrs[attrId]

        fit = Fit(attrMetaGetter)
        ship = Ship(Type(1))
        fit.ship = ship

        attrCharge = attrMetaGetter(1)
        charge1 = Charge(Type(2, attributes={attrCharge.id: 50}))
        charge2 = Charge(Type(3, attributes={attrCharge.id: 200}))

        attrMod = attrMetaGetter(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.other
        info.operator = Operator.postPercent
        info.targetAttributeId = attrCharge.id
        info.sourceType = SourceType.attribute
        info.sourceValue = attrMod.id
        modEffect = Effect(1, categoryId=0)
        modEffect._Effect__infos = {info}
        module = Module(Type(4, effects={modEffect}, attributes={attrMod.id: 20}))
        fit.modulesHigh.append(module)

        # First, check if delayed modifier is applied properly
        module.charge = charge1
        expVal = 60
        self.assertAlmostEqual(charge1.attributes[attrCharge.id], expVal)

        # Then, check if after removal of modifier it's disabled properly,
        # to become enabled once again for other charge
        module.charge = None
        module.charge = charge2
        expVal = 240
        self.assertAlmostEqual(charge2.attributes[attrCharge.id], expVal)
