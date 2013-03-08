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
from eos.const.eve import Category, EffectCategory
from eos.eve.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestOperatorPenaltyImmuneCategory(AttrCalcTestCase):
    """Test that items from several categories are immune to stacking penalty"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = self.ch.attribute(attributeId=1, stackable=0)
        self.srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = self.srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = self.tgtAttr.id
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        self.effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        self.effect.modifiers = (modifier,)
        self.fit = Fit()

    def testShip(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.ship, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=Category.ship, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testCharge(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.charge, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=Category.charge, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testSkill(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.skill, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=Category.skill, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testImplant(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.implant, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=Category.implant, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testSubsystem(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.subsystem, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=Category.subsystem, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testMixed(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.charge, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=Category.implant, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testWithNotImmune(self):
        influenceSource1 = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), categoryId=Category.charge, attributes={self.srcAttr.id: 50}))
        influenceSource2 = IndependentItem(self.ch.type_(typeId=2, effects=(self.effect,), categoryId=None, attributes={self.srcAttr.id: 100}))
        self.fit.items.append(influenceSource1)
        self.fit.items.append(influenceSource2)
        influenceTarget = ShipItem(self.ch.type_(typeId=3, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 300)
        self.fit.items.remove(influenceSource1)
        self.fit.items.remove(influenceSource2)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)
