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
from eos.tests.environment import CacheHandler


class TestTransitionFit(AttrCalcTestCase):
    """
    Test cases when holder is transferred from fit to fit,
    when both fits exist within the same eos instance (i.e.
    holder's item doesn't change).
    """

    def testFitAttrUpdate(self):
        # Here we create 2 separate fits with ships affecting it;
        # each ship affects module with different strength. When we
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
        fit1 = Fit(self.ch)
        fit1.ship = ship1
        fit2 = Fit(self.ch)
        fit2.ship = ship2
        fit1.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr.id), 55)
        fit1.items.remove(module)
        fit1.ship = None
        self.assertLinkBuffersEmpty(fit1)
        fit2.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr.id), 60)
        fit2.ship = None
        fit2.items.remove(module)
        self.assertLinkBuffersEmpty(fit2)

    def testEosAttrUpdate(self):
        # Here we check if attributes are updated if fit changes
        # eos' instance; we do not actually switch eos instance,
        # but we switch cacheHandler, and it should be enough
        cacheHandler1 = CacheHandler()
        cacheHandler2 = CacheHandler()
        srcAttr1 = cacheHandler1.attribute(attributeId=1)
        tgtAttr1 = cacheHandler1.attribute(attributeId=2, maxAttributeId=33)
        cacheHandler1.attribute(attributeId=33, defaultValue=100)
        srcAttr2 = cacheHandler2.attribute(attributeId=1)
        tgtAttr2 = cacheHandler2.attribute(attributeId=2, maxAttributeId=333)
        cacheHandler2.attribute(attributeId=333, defaultValue=500)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = 1
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = 2
        modifier.location = Location.ship
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect1 = cacheHandler1.effect(effectId=1, categoryId=EffectCategory.passive)
        effect1.modifiers = (modifier,)
        effect2 = cacheHandler1.effect(effectId=111, categoryId=EffectCategory.passive)
        effect2.modifiers = (modifier,)
        # Our holders from test environment fo not update undelying
        # item automatically when eos instance is switched, thus we
        # do it manually
        shipItem1 = cacheHandler1.type_(typeId=8, effects=(effect1,), attributes={srcAttr1.id: 10})
        shipItem2 = cacheHandler2.type_(typeId=8, effects=(effect2,), attributes={srcAttr2.id: 20})
        moduleItem1 = cacheHandler1.type_(typeId=4, attributes={tgtAttr1.id: 50})
        moduleItem2 = cacheHandler2.type_(typeId=4, attributes={tgtAttr2.id: 75})
        fit = Fit(cacheHandler1)
        ship = IndependentItem(shipItem1)
        module = ShipItem(moduleItem1)
        fit.ship = ship
        fit.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgtAttr1.id), 55)
        # As we have capped attr, this auxiliary map shouldn't be None
        self.assertIsNotNone(module.attributes._capMap)
        # Make an 'eos switch': remove holders from attributeCalculator
        for holder in (ship, module):
            disabledStates = set(filter(lambda s: s <= holder.state, State))
            fit._linkTracker.disableStates(holder, disabledStates)
            fit._linkTracker.removeHolder(holder)
        # Refresh holders and replace eos
        fit.eos._cacheHandler = cacheHandler2
        ship.attributes.clear()
        ship.item = shipItem2
        module.attributes.clear()
        module.item = moduleItem2
        # When we cleared holders, auxiliary map for capped attrs should be None.
        # Using data in this map, attributes which depend on capping attribute will
        # be cleared. If we don't clear it, there're chances that in new data this
        # capping-capped attribute pair won't exist, thus if attribute with ID which
        # used to cap is changed, it will clear attribute which used to be capped -
        # and we do not want it within scope of new data.
        self.assertIsNone(module.attributes._capMap)
        # Add holders again, when new items are in holders
        for holder in (ship, module):
            fit._linkTracker.addHolder(holder)
            enabledStates = set(filter(lambda s: s <= holder.state, State))
            fit._linkTracker.enableStates(holder, enabledStates)
        # Now we should have calculated value based on both updated attribs
        # if attribs weren't refreshed, we would use old value for modification
        # (10 instead of 20)
        self.assertAlmostEqual(module.attributes.get(tgtAttr2.id), 90)
        fit.ship = None
        fit.items.remove(module)
        self.assertLinkBuffersEmpty(fit)
