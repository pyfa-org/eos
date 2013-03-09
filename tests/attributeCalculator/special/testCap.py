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


class TestCap(AttrCalcTestCase):
    """Test how capped attribute values are processed"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.cappedAttr = self.ch.attribute(attributeId=1, maxAttributeId=2)
        self.cappingAttr = self.ch.attribute(attributeId=2, defaultValue=5)
        self.sourceAttr = self.ch.attribute(attributeId=3)
        # Just to make sure cap is applied to final value, not
        # base, make some basic modification modifier
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = self.sourceAttr.id
        modifier.operator = Operator.postMul
        modifier.targetAttributeId = self.cappedAttr.id
        modifier.location = Location.self_
        modifier.filterType = None
        modifier.filterValue = None
        self.effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def testCapDefault(self):
        # Check that cap is applied properly when holder
        # doesn't have base value of capping attribute
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 5)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testCapOriginal(self):
        # Make sure that holder's own specified attribute
        # value is taken as cap
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6,
                                                                                             self.cappingAttr.id: 2}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 2)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testCapModified(self):
        # Make sure that holder's own specified attribute
        # value is taken as cap, and it's taken with all
        # modifications applied onto it
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = self.sourceAttr.id
        modifier.operator = Operator.postMul
        modifier.targetAttributeId = self.cappingAttr.id
        modifier.location = Location.self_
        modifier.filterType = None
        modifier.filterValue = None
        effect = self.ch.effect(effectId=2, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect, effect), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6,
                                                                                                    self.cappingAttr.id: 0.1}))
        self.fit.items.add(holder)
        # Attr value is 3 * 6 = 18, but cap value is 0.1 * 6 = 0.6
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 0.6)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)

    def testCapUpdate(self):
        # If cap updates, capped attributes should
        # be updated too
        holder = ShipItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.cappedAttr.id: 3, self.sourceAttr.id: 6,
                                                                                      self.cappingAttr.id: 2}))
        self.fit.items.add(holder)
        # Check attribute vs original cap
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 2)
        # Add something which changes capping attribute
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = self.sourceAttr.id
        modifier.operator = Operator.postMul
        modifier.targetAttributeId = self.cappingAttr.id
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect = self.ch.effect(effectId=2, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        capUpdater = IndependentItem(self.ch.type_(typeId=2, effects=(effect,), attributes={self.sourceAttr.id: 3.5}))
        self.fit.items.add(capUpdater)
        # As capping attribute is updated, capped attribute must be updated too
        self.assertAlmostEqual(holder.attributes[self.cappedAttr.id], 7)
        self.fit.items.remove(holder)
        self.fit.items.remove(capUpdater)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)
