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
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestTransitionFit(AttrCalcTestCase):
    """
    Test cases when holder is transferred from fit to fit,
    when both fits exist within the same eos instance (i.e.
    holder's item doesn't change).
    """

    def testAttrUpdate(self):
        # Here we create 2 separate fits with ships affecting it;
        # eaach ship affects module with different strength. When we
        # pass module from one fit to another, its internal attribute
        # storage should be cleared. If it wasn't cleared, we wouldn't
        # be able to get refreshed value of attribute
        srcAttr = self.ch.attribute(attributeId=1)
        tgtAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        ship1 = IndependentItem(self.ch.type_(typeId=1, effects=(effect,), attributes={srcAttr.id: 10}))
        ship2 = IndependentItem(self.ch.type_(typeId=2, effects=(effect,), attributes={srcAttr.id: 20}))
        module = ShipItem(self.ch.type_(typeId=3, attributes={tgtAttr.id: 50}))
        fit1 = Fit()
        fit1.ship = ship1
        fit2 = Fit()
        fit2.ship = ship2
        fit1.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr.id), 55)
        fit1.items.remove(module)
        fit1.ship = None
        self.assertBuffersEmpty(fit1)
        fit2.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr.id), 60)
        fit2.ship = None
        fit2.items.remove(module)
        self.assertBuffersEmpty(fit2)


    def testCapUpdate(self):
        srcAttr = self.ch.attribute(attributeId=1)
        tgtAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        ship1 = IndependentItem(self.ch.type_(typeId=1, effects=(effect,), attributes={srcAttr.id: 10}))
        ship2 = IndependentItem(self.ch.type_(typeId=2, effects=(effect,), attributes={srcAttr.id: 20}))
        module = ShipItem(self.ch.type_(typeId=3, attributes={tgtAttr.id: 50}))
        fit1 = Fit()
        fit1.ship = ship1
        fit2 = Fit()
        fit2.ship = ship2
        fit1.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr.id), 55)
        fit1.items.remove(module)
        fit1.ship = None
        self.assertBuffersEmpty(fit1)
        fit2.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr.id), 60)
        fit2.ship = None
        fit2.items.remove(module)
        self.assertBuffersEmpty(fit2)
