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

from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import Category, EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestOperatorPenaltyImmuneCategory(TestCase):
    """Test that items from several categories are immune to stacking penalty"""

    def setUp(self):
        self.tgtAttr = tgtAttr = Attribute(1, stackable=False)
        self.srcAttr = srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.ship
        info.filterType = FilterType.all_
        info.filterValue = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        self.effect = Effect(1, EffectCategory.passive)
        self.effect._Effect__infos = {info}
        self.fit = Fit(lambda attrId: {tgtAttr.id: tgtAttr, srcAttr.id: srcAttr}[attrId])

    def testShip(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.ship, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.ship, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testCharge(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.charge, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.charge, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testSkill(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.skill, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.skill, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testImplant(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.implant, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.implant, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testSubsystem(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.subsystem, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.subsystem, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testMixed(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.charge, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.implant, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testWithNotImmune(self):
        influenceSource1 = IndependentItem(Type(None, effects={self.effect}, categoryId=Category.charge, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(Type(None, effects={self.effect}, categoryId=None, attributes={self.srcAttr.id: 100}))
        self.fit._addHolder(influenceSource1)
        self.fit._addHolder(influenceSource2)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 300
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))
