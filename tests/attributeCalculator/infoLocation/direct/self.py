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

from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem, SpaceItem


class TestLocationDirectSelf(TestCase):
    """Test location.self (self-reference) for direct modifications"""

    def setUp(self):
        self.tgtAttr = tgtAttr = Attribute(1)
        self.srcAttr = srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.self_
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        self.effect = Effect(1, EffectCategory.passive)
        self.effect._Effect__infos = {info}
        self.fit = Fit(lambda attrId: {tgtAttr.id: tgtAttr, srcAttr.id: srcAttr}[attrId])

    def testIndependent(self):
        holder = IndependentItem(Type(1, effects={self.effect}, attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit._addHolder(holder)
        notExpValue = 100
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")
        # We do not test item removal here, because removed holder (which is
        # both source and target in this test set) essentially becomes
        # detached, which is covered by other tests

    def testCharacter(self):
        holder = CharacterItem(Type(1, effects={self.effect}, attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit._addHolder(holder)
        notExpValue = 100
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")

    def testShip(self):
        holder = ShipItem(Type(1, effects={self.effect}, attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit._addHolder(holder)
        notExpValue = 100
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")

    def testSpace(self):
        holder = SpaceItem(Type(1, effects={self.effect}, attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit._addHolder(holder)
        notExpValue = 100
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")

    def testPositioned(self):
        holder = IndependentItem(Type(1, effects={self.effect}, attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.character = holder
        self.fit._addHolder(holder)
        notExpValue = 100
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")

    def testOther(self):
        # Here we check that self-reference modifies only carrier-item,
        # and nothing else is affected. We position item as character and
        # check character item to also check that items 'belonging' to self
        # are not affected too
        influenceSource = IndependentItem(Type(1, effects={self.effect}, attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.character = influenceSource
        self.fit._addHolder(influenceSource)
        influenceTarget = CharacterItem(Type(2, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        expValue = 100
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must stay unmodified")
