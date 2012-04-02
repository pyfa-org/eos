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


from eos.const import State, Location, Context, Operator
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem, SpaceItem


class TestLocationDirectSelf(AttrCalcTestCase):
    """Test location.self (self-reference) for direct modifications"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        self.srcAttr = srcAttr = Attribute(2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.self_
        modifier.filterType = None
        modifier.filterValue = None
        self.effect = Effect(None, EffectCategory.passive)
        self.effect._modifiers = (modifier,)
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})

    def testIndependent(self):
        holder = IndependentItem(Type(None, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.append(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        # We do not test attribute value after item removal here, because
        # removed holder (which is both source and target in this test set)
        # essentially becomes detached, which is covered by other tests
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testCharacter(self):
        holder = CharacterItem(Type(None, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.append(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testShip(self):
        holder = ShipItem(Type(None, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.append(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testSpace(self):
        holder = SpaceItem(Type(None, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.items.append(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testPositioned(self):
        holder = IndependentItem(Type(None, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.character = holder
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.character = None
        self.assertBuffersEmpty(self.fit)

    def testOther(self):
        # Here we check that self-reference modifies only carrier-item,
        # and nothing else is affected. We position item as character and
        # check character item to also check that items 'belonging' to self
        # are not affected too
        influenceSource = IndependentItem(Type(None, effects=(self.effect,), attributes={self.tgtAttr.id: 100, self.srcAttr.id: 20}))
        self.fit.character = influenceSource
        influenceTarget = CharacterItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.character = None
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)
