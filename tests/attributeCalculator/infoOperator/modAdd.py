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

from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestOperatorAdd(TestCase):
    """Test addition operator"""

    def setUp(self):
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
        info.operator = Operator.modAdd
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        fit = Fit(lambda attrId: {tgtAttr.id: tgtAttr, srcAttr.id: srcAttr}[attrId])
        influenceSource1 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 10}))
        influenceSource2 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: -20}))
        influenceSource3 = IndependentItem(Type(None, effects={effect}, attributes={srcAttr.id: 53}))
        self.influenceTarget = ShipItem(Type(None, attributes={tgtAttr.id: 100}))
        fit._addHolder(influenceSource1)
        fit._addHolder(influenceSource2)
        fit._addHolder(influenceSource3)
        fit._addHolder(self.influenceTarget)

    def testUnpenalized(self):
        self.tgtAttr.stackable = True
        expValue = 143
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))

    def testPenalized(self):
        self.tgtAttr.stackable = False
        expValue = 143
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))
