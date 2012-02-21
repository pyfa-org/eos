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
from eos.eve.const import Attribute as AttributeIDs, EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem
from eos.tests.eosTestCase import EosTestCase


class TestFilterLocationSkillrqSelf(EosTestCase):
    """
    Test location-skill requirement filter, where skill
    requirement references typeID of info carrier
    """

    def setUp(self):
        EosTestCase.setUp(self)
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
        effect._Effect__infos = (info,)
        self.influenceSource = IndependentItem(Type(772, effects=(effect,), attributes={srcAttr.id: 20}))
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        self.fit._addHolder(self.influenceSource)

    def testMatch(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, AttributeIDs.requiredSkill1: 772}))
        self.fit._addHolder(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit._removeHolder(self.influenceSource)

        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)

    def testOtherSkill(self):
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100, AttributeIDs.requiredSkill1: 51}))
        self.fit._addHolder(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
