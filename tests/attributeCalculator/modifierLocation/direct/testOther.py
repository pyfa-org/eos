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


from eos.const.eos import State, Location, Context, Operator
from eos.const.eve import EffectCategory
from eos.data.cache.object.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import IndependentItem, ItemWithOther


class TestLocationDirectOther(AttrCalcTestCase):
    """Test location.other for direct modifications"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = self.ch.attribute(attributeId=1)
        srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = self.tgtAttr.id
        modifier.location = Location.other
        modifier.filterType = None
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        # We added target attribute to influence source for testSelf;
        # currently, eos cannot calculate attributes which are originally
        # missing on item
        self.influenceSource = ItemWithOther(self.ch.type_(typeId=1, effects=(effect,), attributes={self.tgtAttr.id: 100, srcAttr.id: 20}))
        self.fit.items.add(self.influenceSource)

    def testOtherLocation(self):
        influenceTarget = ItemWithOther(self.ch.type_(typeId=2, attributes={self.tgtAttr.id: 100}))
        self.influenceSource.makeOtherLink(influenceTarget)
        self.fit.items.add(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.influenceSource.breakOtherLink(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testSelf(self):
        # Check that source holder isn't modified
        influenceTarget = ItemWithOther(self.ch.type_(typeId=2, attributes={self.tgtAttr.id: 100}))
        self.influenceSource.makeOtherLink(influenceTarget)
        self.fit.items.add(influenceTarget)
        self.assertAlmostEqual(self.influenceSource.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.influenceSource.breakOtherLink(influenceTarget)
        self.fit.items.remove(self.influenceSource)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testOtherHolder(self):
        # Here we check some "random" holder, w/o linking holders
        influenceTarget = IndependentItem(self.ch.type_(typeId=2, attributes={self.tgtAttr.id: 100}))
        self.fit.items.add(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(self.influenceSource)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)
