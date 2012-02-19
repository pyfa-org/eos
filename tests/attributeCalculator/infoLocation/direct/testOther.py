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
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.eosTestCase import EosTestCase


class TestLocationDirectOther(EosTestCase):
    """Test location.other for direct modifications"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.other
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        # We added target attribute to influence source for testSelf;
        # currently, eos cannot calculate attributes which are originally
        # missing on item
        self.influenceSource = IndependentItem(Type(None, effects={effect}, attributes={self.tgtAttr.id: 100, srcAttr.id: 20}))
        self.fit._addHolder(self.influenceSource)

    def testOtherLocation(self):
        influenceTarget = IndependentItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.influenceSource._other = influenceTarget
        influenceTarget._other = self.influenceSource
        self.fit._addHolder(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit._removeHolder(self.influenceSource)
        self.influenceSource._other = None
        influenceTarget._other = None
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)

    def testSelf(self):
        # Check that source holder isn't modified
        influenceTarget = IndependentItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.influenceSource._other = influenceTarget
        influenceTarget._other = self.influenceSource
        self.fit._addHolder(influenceTarget)
        self.assertAlmostEqual(self.influenceSource.attributes[self.tgtAttr.id], 100)

    def testOtherHolder(self):
        # Here we check some "random" holder, w/o assigning
        # _other attribute
        influenceTarget = IndependentItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
