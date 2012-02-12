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
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem
from eos.tests.eosTestCase import EosTestCase


class TestOperatorPostMul(EosTestCase):
    """Test post-multiplication operator"""

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
        info.filterType = FilterType.all_
        info.filterValue = None
        info.operator = Operator.postMul
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        influenceSource1 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 1.2}))
        influenceSource2 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 1.5}))
        influenceSource3 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 0.1}))
        influenceSource4 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 0.75}))
        influenceSource5 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 5}))
        self.influenceTarget = ShipItem(Type(None, attributes={tgtAttr.id: 100}))
        fit._addHolder(influenceSource1)
        fit._addHolder(influenceSource2)
        fit._addHolder(influenceSource3)
        fit._addHolder(influenceSource4)
        fit._addHolder(influenceSource5)
        fit._addHolder(self.influenceTarget)

    def testUnpenalized(self):
        self.tgtAttr.stackable = True
        expValue = 67.5
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testPenalized(self):
        self.tgtAttr.stackable = False
        expValue = 62.5497832
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))
