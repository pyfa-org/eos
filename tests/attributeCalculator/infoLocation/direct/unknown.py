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


from logging import WARNING

from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.eosTestCase import EosTestCase


class TestLocationDirectUnknown(EosTestCase):
    """Test reaction to unknown location specification for direct modification"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        self.srcAttr = srcAttr = Attribute(2)
        self.invalidInfo = invalidInfo = Info()
        invalidInfo.state = State.offline
        invalidInfo.context = Context.local
        invalidInfo.runTime = RunTime.duration
        invalidInfo.gang = False
        invalidInfo.location = 1972
        invalidInfo.filterType = None
        invalidInfo.filterValue = None
        invalidInfo.operator = Operator.postPercent
        invalidInfo.targetAttributeId = tgtAttr.id
        invalidInfo.sourceType = SourceType.attribute
        invalidInfo.sourceValue = srcAttr.id
        self.effect = Effect(None, EffectCategory.passive)
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})

    def testLog(self):
        self.effect._Effect__infos = {self.invalidInfo}
        holder = IndependentItem(Type(754, effects={self.effect}, attributes={self.srcAttr.id: 20}))
        self.fit._addHolder(holder)
        self.assertEqual(len(self.log), 2)
        logRecord = self.log[0]
        self.assertEqual(logRecord.levelno, WARNING)
        expMessage = "malformed info on item 754: unsupported target location 1972 for direct modification"
        self.assertEqual(logRecord.msg, expMessage)
        logRecord = self.log[1]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, expMessage)
        self.fit._removeHolder(holder)
        self.assertEqual(len(self.log), 4)
        logRecord = self.log[2]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, expMessage)
        logRecord = self.log[3]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, expMessage)

    def testCombination(self):
        validInfo = Info()
        validInfo.state = State.offline
        validInfo.context = Context.local
        validInfo.runTime = RunTime.duration
        validInfo.gang = False
        validInfo.location = Location.self_
        validInfo.filterType = None
        validInfo.filterValue = None
        validInfo.operator = Operator.postPercent
        validInfo.targetAttributeId = self.tgtAttr.id
        validInfo.sourceType = SourceType.attribute
        validInfo.sourceValue = self.srcAttr.id
        self.effect._Effect__infos = {self.invalidInfo, validInfo}
        holder = IndependentItem(Type(None, effects={self.effect}, attributes={self.srcAttr.id: 20, self.tgtAttr.id: 100}))
        self.fit._addHolder(holder)
        # Invalid location in info should prevent proper processing of other infos
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
