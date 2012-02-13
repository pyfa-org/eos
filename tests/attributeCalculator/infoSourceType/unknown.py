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

from eos.const import State, Location, FilterType, Context, RunTime, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem
from eos.tests.eosTestCase import EosTestCase


class TestSourceTypeUnknown(EosTestCase):
    """Test how calculator reacts to unknown source type"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
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
        info.sourceType = 56
        info.sourceValue = 37
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        influenceSource = IndependentItem(Type(739, effects={effect}, attributes={srcAttr.id: 20}))
        self.influenceTarget = ShipItem(Type(None, attributes={tgtAttr.id: 50}))
        self.fit._addHolder(influenceSource)
        self.fit._addHolder(self.influenceTarget)

    def testError(self):
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], 50)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertTrue("item 739" in logRecord.msg)
        self.assertTrue("source type 56" in logRecord.msg)

    def testCombination(self):
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.ship
        info.filterType = FilterType.all_
        info.filterValue = None
        info.operator = Operator.postMul
        info.targetAttributeId = self.tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = self.srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        influenceSource = IndependentItem(Type(None, effects={effect}, attributes={self.srcAttr.id: 1.5}))
        self.fit._addHolder(influenceSource)
        # Make sure presence of invalid sourceType doesn't screw
        # calculating value using other infos
        self.assertNotAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], 100)
