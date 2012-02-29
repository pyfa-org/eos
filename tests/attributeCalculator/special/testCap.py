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


from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestCap(AttrCalcTestCase):
    """Test how capped attribute values are processed"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.cappedAttr = cappedAttr = Attribute(1, maxAttributeId=2)
        self.cappingAttr = cappingAttr = Attribute(2, defaultValue=5)
        self.sourceAttr = sourceAttr = Attribute(3)
        # Just to make sure cap is applied to final value, not
        # base, make some basic modification info
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.self_
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postMul
        info.targetAttributeId = cappedAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = sourceAttr.id
        self.effect = Effect(None, EffectCategory.passive)
        self.effect._infos = (info,)
        self.fit = Fit({cappedAttr.id: cappedAttr, cappingAttr.id: cappingAttr, sourceAttr.id: sourceAttr})

    def testCapDefault(self):
        # Check that cap is applied properly when holder
        # doesn't have base value of capping attribute
        holder = IndependentItem(Type(None, effects=(self.effect,), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6}))
        self.fit.items.append(holder)
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 5)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testCapOriginal(self):
        # Make sure that holder's own specified attribute
        # value is taken as cap
        holder = IndependentItem(Type(None, effects=(self.effect,), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6,
                                                                                self.cappingAttr.id: 2}))
        self.fit.items.append(holder)
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 2)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testCapModified(self):
        # Make sure that holder's own specified attribute
        # value is taken as cap, and it's taken with all
        # modifications applied onto it
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.self_
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postMul
        info.targetAttributeId = self.cappingAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = self.sourceAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (info,)
        holder = IndependentItem(Type(None, effects=(self.effect, effect), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6,
                                                                                       self.cappingAttr.id: 0.1}))
        self.fit.items.append(holder)
        # Attr value is 3 * 6 = 18, but cap value is 0.1 * 6 = 0.6
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 0.6)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testCapUpdate(self):
        # If cap updates, capped attributes should
        # be updated too
        holder = ShipItem(Type(None, effects=(self.effect,), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6,
                                                                         self.cappingAttr.id: 2}))
        self.fit.items.append(holder)
        # Check attribute vs original cap
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 2)
        # Add something which changes capping attribute
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.ship
        info.filterType = FilterType.all_
        info.filterValue = None
        info.operator = Operator.postMul
        info.targetAttributeId = self.cappingAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = self.sourceAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (info,)
        capUpdater = IndependentItem(Type(None, effects=(effect,), attributes={self.sourceAttr.id: 3.5}))
        self.fit.items.append(capUpdater)
        # As capping attribute is updated, capped attribute must be updated too
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 7)
        self.fit.items.remove(holder)
        self.fit.items.remove(capUpdater)
        self.assertBuffersEmpty(self.fit)
