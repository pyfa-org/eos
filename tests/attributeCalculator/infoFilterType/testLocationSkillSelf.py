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


from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType, InvType
from eos.eve.attribute import Attribute
from eos.eve.const import Attribute as ConstAttribute, EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestFilterLocationSkillrqSelf(AttrCalcTestCase):
    """
    Test location-skill requirement filter, where skill
    requirement references typeID of info carrier
    """

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.ship
        info.filterType = FilterType.skill
        info.filterValue = InvType.self_
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (info,)
        self.influenceSource = IndependentItem(Type(772, effects=(effect,), attributes={srcAttr.id: 20}))
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        self.fit.items.append(self.influenceSource)

    def testMatch1(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill1: 772, ConstAttribute.requiredSkill1Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testMatch2(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill2: 772, ConstAttribute.requiredSkill2Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testMatch3(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill3: 772, ConstAttribute.requiredSkill3Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testMatch4(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill4: 772, ConstAttribute.requiredSkill4Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testMatch5(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill5: 772, ConstAttribute.requiredSkill5Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testMatch6(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill6: 772, ConstAttribute.requiredSkill6Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testOtherSkill(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, ConstAttribute.requiredSkill1: 51, ConstAttribute.requiredSkill1Level: 1}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)
