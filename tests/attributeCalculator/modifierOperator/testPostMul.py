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


from eos.const import State, Location, Context, FilterType, Operator
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestOperatorPostMul(AttrCalcTestCase):
    """Test post-multiplication operator"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postMul
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect = Effect(None, EffectCategory.passive)
        effect._modifiers = (modifier,)
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        self.influenceSource1 = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 1.2}))
        self.influenceSource2 = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 1.5}))
        self.influenceSource3 = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 0.1}))
        self.influenceSource4 = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 0.75}))
        self.influenceSource5 = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 5}))
        self.influenceTarget = ShipItem(Type(None, attributes={tgtAttr.id: 100}))
        self.fit.items.append(self.influenceSource1)
        self.fit.items.append(self.influenceSource2)
        self.fit.items.append(self.influenceSource3)
        self.fit.items.append(self.influenceSource4)
        self.fit.items.append(self.influenceSource5)
        self.fit.items.append(self.influenceTarget)

    def testUnpenalized(self):
        self.tgtAttr.stackable = True
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], 67.5)
        self.fit.items.remove(self.influenceSource1)
        self.fit.items.remove(self.influenceSource2)
        self.fit.items.remove(self.influenceSource3)
        self.fit.items.remove(self.influenceSource4)
        self.fit.items.remove(self.influenceSource5)
        self.fit.items.remove(self.influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testPenalized(self):
        self.tgtAttr.stackable = False
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], 62.5497832)
        self.fit.items.remove(self.influenceSource1)
        self.fit.items.remove(self.influenceSource2)
        self.fit.items.remove(self.influenceSource3)
        self.fit.items.remove(self.influenceSource4)
        self.fit.items.remove(self.influenceSource5)
        self.fit.items.remove(self.influenceTarget)
        self.assertBuffersEmpty(self.fit)
