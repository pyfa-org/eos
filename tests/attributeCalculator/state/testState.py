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
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, fitTrackedData
from eos.tests.eosTestCase import EosTestCase


class TestStateSwitching(EosTestCase):
    """Test holder state switching and info states"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr1 = Attribute(2)
        srcAttr2 = Attribute(3)
        srcAttr3 = Attribute(4)
        srcAttr4 = Attribute(5)
        infoOff = Info()
        infoOff.state = State.offline
        infoOff.context = Context.local
        infoOff.runTime = RunTime.duration
        infoOff.gang = False
        infoOff.location = Location.self_
        infoOff.filterType = None
        infoOff.filterValue = None
        infoOff.operator = Operator.postMul
        infoOff.targetAttributeId = tgtAttr.id
        infoOff.sourceType = SourceType.attribute
        infoOff.sourceValue = srcAttr1.id
        infoOn = Info()
        infoOn.state = State.online
        infoOn.context = Context.local
        infoOn.runTime = RunTime.duration
        infoOn.gang = False
        infoOn.location = Location.self_
        infoOn.filterType = None
        infoOn.filterValue = None
        infoOn.operator = Operator.postMul
        infoOn.targetAttributeId = tgtAttr.id
        infoOn.sourceType = SourceType.attribute
        infoOn.sourceValue = srcAttr2.id
        infoAct = Info()
        infoAct.state = State.active
        infoAct.context = Context.local
        infoAct.runTime = RunTime.duration
        infoAct.gang = False
        infoAct.location = Location.self_
        infoAct.filterType = None
        infoAct.filterValue = None
        infoAct.operator = Operator.postMul
        infoAct.targetAttributeId = tgtAttr.id
        infoAct.sourceType = SourceType.attribute
        infoAct.sourceValue = srcAttr3.id
        infoOver = Info()
        infoOver.state = State.overload
        infoOver.context = Context.local
        infoOver.runTime = RunTime.duration
        infoOver.gang = False
        infoOver.location = Location.self_
        infoOver.filterType = None
        infoOver.filterValue = None
        infoOver.operator = Operator.postMul
        infoOver.targetAttributeId = tgtAttr.id
        infoOver.sourceType = SourceType.attribute
        infoOver.sourceValue = srcAttr4.id
        # Overload category will make sure that holder can enter all states
        effect = Effect(None, EffectCategory.overload)
        effect._infos = (infoOff, infoOn, infoAct, infoOver)
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr1.id: srcAttr1, srcAttr2.id: srcAttr2,
                        srcAttr3.id: srcAttr3, srcAttr4.id: srcAttr4})
        self.holder = IndependentItem(Type(None, effects=(effect,), attributes={self.tgtAttr.id: 100, srcAttr1.id: 1.1,
                                                                                srcAttr2.id: 1.3, srcAttr3.id: 1.5,
                                                                                srcAttr4.id: 1.7}))

    def testFitOffline(self):
        self.holder.state = State.offline
        self.fit._addHolder(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 110)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testFitOnline(self):
        self.holder.state = State.online
        self.fit._addHolder(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 143)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testFitActive(self):
        self.holder.state = State.active
        self.fit._addHolder(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 214.5)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testFitOverloaded(self):
        self.holder.state = State.overload
        self.fit._addHolder(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 364.65)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testSwitchUpSingle(self):
        self.holder.state = State.offline
        self.fit._addHolder(self.holder)
        self.holder.state = State.online
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 143)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testSwitchUpMultiple(self):
        self.holder.state = State.online
        self.fit._addHolder(self.holder)
        self.holder.state = State.overload
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 364.65)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testSwitchDownSingle(self):
        self.holder.state = State.overload
        self.fit._addHolder(self.holder)
        self.holder.state = State.active
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 214.5)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)

    def testSwitchDownMultiple(self):
        self.holder.state = State.active
        self.fit._addHolder(self.holder)
        self.holder.state = State.offline
        self.assertAlmostEqual(self.holder.attributes[self.tgtAttr.id], 110)
        self.fit._removeHolder(self.holder)
        self.assertEqual(fitTrackedData(self.fit), 0)
