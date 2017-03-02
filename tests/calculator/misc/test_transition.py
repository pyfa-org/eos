# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from eos.fit.message import EnableServices, DisableServices
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import Fit, IndependentItem, ShipDomainItem
from tests.environment import CacheHandler


class TestTransitionFit(CalculatorTestCase):
    """
    Test cases when item is transferred from fit to fit, when both
    fits have source assigned (i.e. item's eve type doesn't change).
    """

    def test_fit_attr_update(self):
        # Here we create 2 separate fits with ships affecting it;
        # each ship affects module with different strength. When we
        # pass module from one fit to another, its internal attribute
        # storage should be cleared. If it wasn't cleared, we wouldn't
        # be able to get refreshed value of attribute
        src_attr = self.ch.attribute(attribute_id=1)
        tgt_attr = self.ch.attribute(attribute_id=2)
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        ship1 = IndependentItem(self.ch.type(type_id=1, effects=(effect,), attributes={src_attr.id: 10}))
        ship2 = IndependentItem(self.ch.type(type_id=2, effects=(effect,), attributes={src_attr.id: 20}))
        module = ShipDomainItem(self.ch.type(type_id=3, attributes={tgt_attr.id: 50}))
        fit1 = Fit(self.ch)
        fit1.ship = ship1
        fit2 = Fit(self.ch)
        fit2.ship = ship2
        fit1.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgt_attr.id), 55)
        fit1.items.remove(module)
        fit1.ship = None
        self.assert_calculator_buffers_empty(fit1)
        fit2.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgt_attr.id), 60)
        fit2.ship = None
        fit2.items.remove(module)
        self.assert_calculator_buffers_empty(fit2)

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
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=2,
            operator=ModifierOperator.post_percent,
            src_attr=1
        )
        effect1 = cache_handler1.effect(effect_id=1, category=EffectCategory.passive)
        effect1.modifiers = (modifier,)
        effect2 = cache_handler1.effect(effect_id=111, category=EffectCategory.passive)
        effect2.modifiers = (modifier,)
        # Our items from test environment do not update undelying eve type
        # automatically when source is changed, thus we do it manually
        ship_eve_type1 = cache_handler1.type(type_id=8, effects=(effect1,), attributes={src_attr1.id: 10})
        ship_eve_type2 = cache_handler2.type(type_id=8, effects=(effect2,), attributes={src_attr2.id: 20})
        module_eve_type1 = cache_handler1.type(type_id=4, attributes={tgt_attr1.id: 50})
        module_eve_type2 = cache_handler2.type(type_id=4, attributes={tgt_attr2.id: 75})
        fit = Fit(cache_handler1)
        ship = IndependentItem(ship_eve_type1)
        module = ShipDomainItem(module_eve_type1)
        fit.ship = ship
        fit.items.add(module)
        self.assertAlmostEqual(module.attributes.get(tgt_attr1.id), 55)
        # As we have capped attr, this auxiliary map shouldn't be None
        self.assertGreater(len(module.attributes._cap_map), 0)
        # Make an 'source switch': disable services
        fit._calculator._notify(DisableServices(items=(ship, module)))
        # Refresh items and replace source
        fit.source.cache_handler = cache_handler2
        ship.attributes.clear()
        ship._eve_type = ship_eve_type2
        module.attributes.clear()
        module._eve_type = module_eve_type2
        # When we cleared items, auxiliary map for capped attrs should be None.
        # Using data in this map, attributes which depend on capping attribute will
        # be cleared. If we don't clear it, there're chances that in new data this
        # capping-capped attribute pair won't exist, thus if attribute with ID which
        # used to cap is changed, it will clear attribute which used to be capped -
        # and we do not want it within scope of new data.
        self.assertEqual(len(module.attributes._cap_map), 0)
        # Enable services once switch is complete
        fit._calculator._notify(EnableServices(items=(ship, module)))
        # Now we should have calculated value based on both updated attribs
        # if attribs weren't refreshed, we would use old value for modification
        # (10 instead of 20)
        self.assertAlmostEqual(module.attributes.get(tgt_attr2.id), 90)
        fit.ship = None
        fit.items.remove(module)
        self.assert_calculator_buffers_empty(fit)
