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
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem, SpaceItem


class TestLocationDirectSelf(AttrCalcTestCase):
    """Test location.self (self-reference) for direct modifications"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = self.ch.attribute(attributeId=1)
        self.srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = self.srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = self.tgtAttr.id
        modifier.location = Location.self_
        modifier.filterType = None
        modifier.filterValue = None
        self.effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        self.effect.modifiers = (modifier,)
        self.fit = Fit()

    def testIndependent(self):
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        # We do not test attribute value after item removal here, because
        # removed holder (which is both source and target in this test set)
        # essentially becomes detached, which is covered by other tests
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testCharacter(self):
        holder = CharacterItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testShip(self):
        holder = ShipItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testSpace(self):
        holder = SpaceItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testPositioned(self):
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.character = holder
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.character = None
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testOther(self):
        # Here we check that self-reference modifies only carrier-item,
        # and nothing else is affected. We position item as character and
        # check character item to also check that items 'belonging' to self
        # are not affected too
        influenceSource = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.character = influenceSource
        influenceTarget = CharacterItem(self.ch.type_(typeId=2, attributes={self.tgtAttr.id: 100}))
        self.fit.items.add(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.character = None
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)
