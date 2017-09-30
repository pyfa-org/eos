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


from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategory
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestSourceSwitch(CalculatorTestCase):

    def test_switch_item(self):
        # Here we create 2 separate fits with ships affecting it;
        # each ship affects module with different strength. When we
        # pass module from one fit to another, its internal attribute
        # storage should be cleared. If it wasn't cleared, we wouldn't
        # be able to get refreshed value of attribute
        # Setup
        src_attr_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=src_attr_id)
        self.ch2.attribute(attribute_id=src_attr_id)
        tgt_attr_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=tgt_attr_id)
        self.ch2.attribute(attribute_id=tgt_attr_id)
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr_id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr_id
        )
        effect_id = self.allocate_effect_id(self.ch, self.ch2)
        effect_src1 = self.ch.effect(effect_id=effect_id, category=EffectCategory.passive, modifiers=[modifier])
        effect_src2 = self.ch2.effect(effect_id=effect_id, category=EffectCategory.passive, modifiers=[modifier])
        ship_eve_type_id = self.allocate_type_id(self.ch, self.ch2)
        ship1 = Ship(self.ch.type(type_id=ship_eve_type_id, attributes={src_attr_id: 10}, effects=[effect_src1]).id)
        ship2 = Ship(self.ch2.type(type_id=ship_eve_type_id, attributes={src_attr_id: 20}, effects=[effect_src2]).id)
        item_eve_type_id = self.allocate_type_id(self.ch, self.ch2)
        self.ch.type(type_id=item_eve_type_id, attributes={tgt_attr_id: 50})
        self.ch2.type(type_id=item_eve_type_id, attributes={tgt_attr_id: 50})
        item = Rig(item_eve_type_id)
        fit1 = Fit('src1')
        fit1.ship = ship1
        fit2 = Fit('src2')
        fit2.ship = ship2
        fit1.rigs.add(item)
        self.assertAlmostEqual(item.attributes.get(tgt_attr_id), 55)
        # Action
        fit1.rigs.remove(item)
        fit2.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes.get(tgt_attr_id), 60)
        # Cleanup
        self.assert_fit_buffers_empty(fit1)
        self.assert_fit_buffers_empty(fit2)

    def test_switch_fit(self):
        # Here we check if attributes are updated if fit gets new
        # source instance
        # Setup
        src_attr_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=src_attr_id)
        self.ch2.attribute(attribute_id=src_attr_id)
        tgt_attr_id = self.allocate_attribute_id(self.ch, self.ch2)
        max_attr_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=tgt_attr_id, max_attribute=max_attr_id)
        self.ch2.attribute(attribute_id=tgt_attr_id, max_attribute=max_attr_id)
        self.ch.attribute(attribute_id=max_attr_id, default_value=54.5)
        self.ch2.attribute(attribute_id=max_attr_id, default_value=88)
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr_id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr_id
        )
        effect_id = self.allocate_effect_id(self.ch, self.ch2)
        effect_src1 = self.ch.effect(effect_id=effect_id, category=EffectCategory.passive, modifiers=[modifier])
        effect_src2 = self.ch2.effect(effect_id=effect_id, category=EffectCategory.passive, modifiers=[modifier])
        ship_eve_type_id = self.allocate_type_id(self.ch, self.ch2)
        self.ch.type(type_id=ship_eve_type_id, attributes={src_attr_id: 10}, effects=[effect_src1])
        self.ch2.type(type_id=ship_eve_type_id, attributes={src_attr_id: 20}, effects=[effect_src2])
        item_eve_type_id = self.allocate_type_id(self.ch, self.ch2)
        self.ch.type(type_id=item_eve_type_id, attributes={tgt_attr_id: 50})
        self.ch2.type(type_id=item_eve_type_id, attributes={tgt_attr_id: 75})
        fit = Fit()
        ship = Ship(ship_eve_type_id)
        item = Rig(item_eve_type_id)
        fit.ship = ship
        fit.rigs.add(item)
        # 50 * 1.1, but capped at 54.5
        self.assertAlmostEqual(item.attributes.get(tgt_attr_id), 54.5)
        # Action
        fit.source = 'src2'
        # Verification
        # 75 * 1.2, but capped at 88
        self.assertAlmostEqual(item.attributes.get(tgt_attr_id), 88)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
