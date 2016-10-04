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
from eos.const.eve import Category, EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem, ShipItem


class TestOperatorPenaltyImmuneCategory(AttrCalcTestCase):
    """Test that items from several categories are immune to stacking penalty"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1, stackable=0)
        self.src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        modifier.domain = Domain.ship
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_ship(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.ship, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=Category.ship, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_charge(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.charge, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=Category.charge, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_skill(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.skill, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=Category.skill, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_implant(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.implant, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=Category.implant, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_subsystem(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.subsystem, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=Category.subsystem, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_mixed(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.charge, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=Category.implant, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_with_not_immune(self):
        influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), category=Category.charge, attributes={self.src_attr.id: 50}))
        influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(self.effect,), category=None, attributes={self.src_attr.id: 100}))
        self.fit.items.add(influence_source1)
        self.fit.items.add(influence_source2)
        influence_target = ShipItem(self.ch.type_(type_id=3, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 300)
        self.fit.items.remove(influence_source1)
        self.fit.items.remove(influence_source2)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
