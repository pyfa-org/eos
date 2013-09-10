#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from eos.const.eos import State, Location, Context, FilterType, Operator
from eos.const.eve import EffectCategory
from eos.data.cache.object.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import IndependentItem, ShipItem


class TestOperatorPostDiv(AttrCalcTestCase):
    """Test post-division operator"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = self.ch.attribute(attributeId=1)
        srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postDiv
        modifier.targetAttributeId = self.tgtAttr.id
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        self.influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(effect,), attributes={srcAttr.id: 1.2}))
        self.influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(effect,), attributes={srcAttr.id: 1.5}))
        self.influenceSource3 = IndependentItem(self.ch.type_(typeId=3, effects=(effect,), attributes={srcAttr.id: 0.1}))
        self.influenceSource4 = IndependentItem(self.ch.type_(typeId=4, effects=(effect,), attributes={srcAttr.id: 0.75}))
        self.influenceSource5 = IndependentItem(self.ch.type_(typeId=5, effects=(effect,), attributes={srcAttr.id: 5}))
        self.influenceTarget = ShipItem(self.ch.type_(typeId=6, attributes={self.tgtAttr.id: 100}))
        self.fit.items.add(self.influenceSource1)
        self.fit.items.add(self.influenceSource2)
        self.fit.items.add(self.influenceSource3)
        self.fit.items.add(self.influenceSource4)
        self.fit.items.add(self.influenceSource5)
        self.fit.items.add(self.influenceTarget)

    def testUnpenalized(self):
        self.tgtAttr.stackable = True
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], 148.1481481)
        self.fit.items.remove(self.influenceSource1)
        self.fit.items.remove(self.influenceSource2)
        self.fit.items.remove(self.influenceSource3)
        self.fit.items.remove(self.influenceSource4)
        self.fit.items.remove(self.influenceSource5)
        self.fit.items.remove(self.influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertLinkBuffersEmpty(self.fit)

    def testPenalized(self):
        self.tgtAttr.stackable = False
        self.assertAlmostEqual(self.influenceTarget.attributes[self.tgtAttr.id], 165.7908726)
        self.fit.items.remove(self.influenceSource1)
        self.fit.items.remove(self.influenceSource2)
        self.fit.items.remove(self.influenceSource3)
        self.fit.items.remove(self.influenceSource4)
        self.fit.items.remove(self.influenceSource5)
        self.fit.items.remove(self.influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertLinkBuffersEmpty(self.fit)
