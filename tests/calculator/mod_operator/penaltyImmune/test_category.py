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


from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Category, EffectCategory
from eos.fit.calculator.modifier import DogmaModifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, ShipDomainItem


class TestOperatorPenaltyImmuneCategory(CalculatorTestCase):
    """
    Test that items with eve types from several categories
    are immune to stacking penalty
    """

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1, stackable=0)
        self.src_attr = self.ch.attribute(attribute_id=2)
        modifier = DogmaModifier()
        modifier.state = State.offline
        modifier.tgt_filter = ModifierTargetFilter.domain
        modifier.tgt_domain = ModifierDomain.ship
        modifier.tgt_attr = self.tgt_attr.id
        modifier.operator = ModifierOperator.post_percent
        modifier.src_attr = self.src_attr.id
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_ship(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.ship,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=Category.ship,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_charge(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.charge,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=Category.charge,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_skill(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.skill,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=Category.skill,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_implant(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.implant,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=Category.implant,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_subsystem(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.subsystem,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=Category.subsystem,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_mixed(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.charge,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=Category.implant,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_with_not_immune(self):
        influence_source1 = IndependentItem(self.ch.type(
            type_id=1, effects=(self.effect,), category=Category.charge,
            attributes={self.src_attr.id: 50}
        ))
        influence_source2 = IndependentItem(self.ch.type(
            type_id=2, effects=(self.effect,), category=None,
            attributes={self.src_attr.id: 100}
        ))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipDomainItem(self.ch.type(type_id=3, attributes={self.tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        # Cleanup
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
