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


from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.environment import Logger


class TestSourceAttrAbsent(AttrCalcTestCase):
    """Test how calculator reacts to source attribute which is absent"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        self.absAttr = absAttr = Attribute(2)
        self.srcAttr = srcAttr = Attribute(3)
        self.invalidInfo = invalidInfo = Info()
        invalidInfo.state = State.offline
        invalidInfo.context = Context.local
        invalidInfo.runTime = RunTime.duration
        invalidInfo.gang = False
        invalidInfo.location = Location.self_
        invalidInfo.filterType = None
        invalidInfo.filterValue = None
        invalidInfo.operator = Operator.postPercent
        invalidInfo.targetAttributeId = tgtAttr.id
        invalidInfo.sourceType = SourceType.attribute
        invalidInfo.sourceValue = absAttr.id
        self.effect = Effect(None, EffectCategory.passive)
        self.fit = Fit({tgtAttr.id: tgtAttr, absAttr.id: absAttr, srcAttr.id: srcAttr})

    def testLog(self):
        self.effect._infos = (self.invalidInfo,)
        holder = IndependentItem(Type(529, effects=(self.effect,), attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(holder)
        self.assertAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        # Two errors are written to log: first notifies about
        # attempt to access attribute which cannot be calculated,
        # second one is actual error about source value
        self.assertEqual(len(self.log), 2)
        logRecord = self.log[1]
        self.assertEqual(logRecord.name, "eos_test.attributeCalculator")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "malformed source value None on item 529")
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testCombination(self):
        validInfo = Info()
        validInfo.state = State.offline
        validInfo.context = Context.local
        validInfo.runTime = RunTime.duration
        validInfo.gang = False
        validInfo.location = Location.self_
        validInfo.filterType = None
        validInfo.filterValue = None
        validInfo.operator = Operator.postMul
        validInfo.targetAttributeId = self.tgtAttr.id
        validInfo.sourceType = SourceType.attribute
        validInfo.sourceValue = self.srcAttr.id
        self.effect._infos = (self.invalidInfo, validInfo)
        holder = IndependentItem(Type(None, effects=(self.effect,), attributes={self.srcAttr.id: 1.5, self.tgtAttr.id: 100}))
        self.fit.items.append(holder)
        # Invalid source value shouldn't screw whole calculation process
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)
