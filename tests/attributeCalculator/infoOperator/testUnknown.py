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


class TestOperatorUnknown(AttrCalcTestCase):
    """Test unknown operator type"""

    def testLogOther(self):
        # Check how unknown operator value influences
        # attribute calculator
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        invalidInfo = Info()
        invalidInfo.state = State.offline
        invalidInfo.context = Context.local
        invalidInfo.runTime = RunTime.duration
        invalidInfo.gang = False
        invalidInfo.location = Location.self_
        invalidInfo.filterType = None
        invalidInfo.filterValue = None
        invalidInfo.operator = 1008
        invalidInfo.targetAttributeId = tgtAttr.id
        invalidInfo.sourceType = SourceType.attribute
        invalidInfo.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (invalidInfo,)
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        holder = IndependentItem(Type(83, effects=(effect,), attributes={srcAttr.id: 1.2, tgtAttr.id: 100}))
        fit.items.append(holder)
        self.assertAlmostEqual(holder.attributes[tgtAttr.id], 100)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.attributeCalculator")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "malformed info on item 83: unknown operator 1008")
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testLogUnorderableCombination(self):
        # Check how non-orderable operator value influences
        # attribute calculator. Previously, bug in calculation
        # method made it to crash
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        invalidInfo = Info()
        invalidInfo.state = State.offline
        invalidInfo.context = Context.local
        invalidInfo.runTime = RunTime.duration
        invalidInfo.gang = False
        invalidInfo.location = Location.self_
        invalidInfo.filterType = None
        invalidInfo.filterValue = None
        invalidInfo.operator = None
        invalidInfo.targetAttributeId = tgtAttr.id
        invalidInfo.sourceType = SourceType.attribute
        invalidInfo.sourceValue = srcAttr.id
        validInfo = Info()
        validInfo.state = State.offline
        validInfo.context = Context.local
        validInfo.runTime = RunTime.duration
        validInfo.gang = False
        validInfo.location = Location.self_
        validInfo.filterType = None
        validInfo.filterValue = None
        validInfo.operator = Operator.postMul
        validInfo.targetAttributeId = tgtAttr.id
        validInfo.sourceType = SourceType.attribute
        validInfo.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (invalidInfo, validInfo)
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        holder = IndependentItem(Type(83, effects=(effect,), attributes={srcAttr.id: 1.2, tgtAttr.id: 100}))
        fit.items.append(holder)
        self.assertAlmostEqual(holder.attributes[tgtAttr.id], 120)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.attributeCalculator")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "malformed info on item 83: unknown operator None")
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testCombination(self):
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        invalidInfo = Info()
        invalidInfo.state = State.offline
        invalidInfo.context = Context.local
        invalidInfo.runTime = RunTime.duration
        invalidInfo.gang = False
        invalidInfo.location = Location.self_
        invalidInfo.filterType = None
        invalidInfo.filterValue = None
        invalidInfo.operator = 1008
        invalidInfo.targetAttributeId = tgtAttr.id
        invalidInfo.sourceType = SourceType.attribute
        invalidInfo.sourceValue = srcAttr.id
        validInfo = Info()
        validInfo.state = State.offline
        validInfo.context = Context.local
        validInfo.runTime = RunTime.duration
        validInfo.gang = False
        validInfo.location = Location.self_
        validInfo.filterType = None
        validInfo.filterValue = None
        validInfo.operator = Operator.postMul
        validInfo.targetAttributeId = tgtAttr.id
        validInfo.sourceType = SourceType.attribute
        validInfo.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (invalidInfo, validInfo)
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        holder = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 1.5, tgtAttr.id: 100}))
        fit.items.append(holder)
        # Make sure presence of invalid operator doesn't prevent
        # from calculating value based on valid infos
        self.assertNotAlmostEqual(holder.attributes[tgtAttr.id], 100)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)
