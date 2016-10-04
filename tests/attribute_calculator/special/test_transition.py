# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from eos.const.eos import State, Domain, Scope, FilterType, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import Fit, IndependentItem, ShipItem
from tests.environment import CacheHandler


class TestTransitionFit(AttrCalcTestCase):
    """
    Test cases when holder is transferred from fit to fit, when both
    fits have source assigned (i.e. holder's item doesn't change).
    """

    def test_fit_attr_update(self):
        # Here we create 2 separate fits with ships affecting it;
        # each ship affects module with different strength. When we
        # pass module from one fit to another, its internal attribute
        # storage should be cleared. If it wasn't cleared, we wouldn't
        # be able to get refreshed value of attribute
        src_attr = self.ch.attribute(attribute_id=1)
        tgt_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = tgt_attr.id
        modifier.domain = Domain.ship
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        ship1 = IndependentItem(self.ch.type_(type_id=1, effects=(effect,), attributes={src_attr.id: 10}))
        ship2 = IndependentItem(self.ch.type_(type_id=2, effects=(effect,), attributes={src_attr.id: 20}))
        module = ShipItem(self.ch.type_(type_id=3, attributes={tgt_attr.id: 50}))
        fit1 = Fit(self.ch)
        fit1.ship = ship1
        fit2 = Fit(self.ch)
        fit2.ship = ship2
        fit1.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgt_attr.id), 55)
        fit1.items.remove(module)
        fit1.ship = None
        self.assert_link_buffers_empty(fit1)
        fit2.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgt_attr.id), 60)
        fit2.ship = None
        fit2.items.remove(module)
        self.assert_link_buffers_empty(fit2)

    def test_source_attr_update(self):
        # Here we check if attributes are updated if fit gets new
        # source instance; we do not actually switch source but we
        # switch cache_handler, and it should be enough
        cache_handler1 = CacheHandler()
        cache_handler2 = CacheHandler()
        src_attr1 = cache_handler1.attribute(attribute_id=1)
        tgt_attr1 = cache_handler1.attribute(attribute_id=2, max_attribute=33)
        cache_handler1.attribute(attribute_id=33, default_value=100)
        src_attr2 = cache_handler2.attribute(attribute_id=1)
        tgt_attr2 = cache_handler2.attribute(attribute_id=2, max_attribute=333)
        cache_handler2.attribute(attribute_id=333, default_value=500)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = 1
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = 2
        modifier.domain = Domain.ship
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        effect1 = cache_handler1.effect(effect_id=1, category=EffectCategory.passive)
        effect1.modifiers = (modifier,)
        effect2 = cache_handler1.effect(effect_id=111, category=EffectCategory.passive)
        effect2.modifiers = (modifier,)
        # Our holders from test environment fo not update undelying
        # item automatically when source is changed, thus we do it
        # manually
        ship_item1 = cache_handler1.type_(type_id=8, effects=(effect1,), attributes={src_attr1.id: 10})
        ship_item2 = cache_handler2.type_(type_id=8, effects=(effect2,), attributes={src_attr2.id: 20})
        module_item1 = cache_handler1.type_(type_id=4, attributes={tgt_attr1.id: 50})
        module_item2 = cache_handler2.type_(type_id=4, attributes={tgt_attr2.id: 75})
        fit = Fit(cache_handler1)
        ship = IndependentItem(ship_item1)
        module = ShipItem(module_item1)
        fit.ship = ship
        fit.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgt_attr1.id), 55)
        # As we have capped attr, this auxiliary map shouldn't be None
        self.assertIsNotNone(module.attributes._cap_map)
        # Make an 'source switch': remove holders from attribute_calculator
        for holder in (ship, module):
            disabled_states = set(filter(lambda s: s <= holder.state, State))
            fit._link_tracker.disable_states(holder, disabled_states)
            fit._link_tracker.remove_holder(holder)
        # Refresh holders and replace source
        fit.source.cache_handler = cache_handler2
        ship.attributes.clear()
        ship.item = ship_item2
        module.attributes.clear()
        module.item = module_item2
        # When we cleared holders, auxiliary map for capped attrs should be None.
        # Using data in this map, attributes which depend on capping attribute will
        # be cleared. If we don't clear it, there're chances that in new data this
        # capping-capped attribute pair won't exist, thus if attribute with ID which
        # used to cap is changed, it will clear attribute which used to be capped -
        # and we do not want it within scope of new data.
        self.assertIsNone(module.attributes._cap_map)
        # Add holders again, when new items are in holders
        for holder in (ship, module):
            fit._link_tracker.add_holder(holder)
            enabled_states = set(filter(lambda s: s <= holder.state, State))
            fit._link_tracker.enable_states(holder, enabled_states)
        # Now we should have calculated value based on both updated attribs
        # if attribs weren't refreshed, we would use old value for modification
        # (10 instead of 20)
        self.assertAlmostEqual(module.attributes.get(tgt_attr2.id), 90)
        fit.ship = None
        fit.items.remove(module)
        self.assert_link_buffers_empty(fit)
