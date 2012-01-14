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
from eos.fit import Fit, Ship, Module, Charge

class TestModuleAffectsCharge(TestCase):

    def testAttrCalc(self):
        fit = Fit()
        ship = Ship(InvType(1, None, None, {}, {}, {}))
        fit.ship = ship

        attrCharge = Attribute(1, 1, 0)
        chargeType = InvType(2, None, None, {}, {attrCharge.id: 50}, {attrCharge.id: attrCharge})
        charge1 = Charge(chargeType)
        charge2 = Charge(chargeType)

        attrMod = Attribute(2, 1, 0)
        info = EffectInfo()
        info.type = const.infoDuration
        info.location = const.locOther
        info.operator = const.optrPostPercent
        info.targetAttribute = attrCharge.id
        info.sourceType = const.srcAttr
        info.sourceValue = attrMod.id
        modEffect = Effect(1, None, None, 0, 0)
        modEffect._Effect__infos = {info}
        module = Module(InvType(3, None, None, {modEffect}, {attrMod.id: 20}, {attrMod.id: attrMod}))
        fit.modules.append(module)

        # First, check if delayed modifier is applied properly
        module.charge = charge1
        expVal = 60
        self.assertAlmostEqual(charge1.attributes[attrCharge.id], expVal)

        # Then, check if after removal of modifier it's disabled properly,
        # to become enabled once again for other charge
        module.charge = None
        module.charge = charge2
        self.assertAlmostEqual(charge2.attributes[attrCharge.id], expVal)
