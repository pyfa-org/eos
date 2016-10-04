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


from eos.const.eos import State, Domain, Scope, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem, CharacterItem, ShipItem, SpaceItem


class TestDomainDirectSelf(AttrCalcTestCase):
    """Test domain.self (self-reference) for direct modifications"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        self.src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        modifier.domain = Domain.self_
        modifier.filter_type = None
        modifier.filter_value = None
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_independent(self):
        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgt_attr.id], 100)
        # We do not test attribute value after item removal here, because
        # removed holder (which is both source and target in this test set)
        # essentially becomes detached, which is covered by other tests
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_character(self):
        holder = CharacterItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_ship(self):
        holder = ShipItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_space(self):
        holder = SpaceItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.items.add(holder)
        self.assertNotAlmostEqual(holder.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_positioned(self):
        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.character = holder
        self.assertNotAlmostEqual(holder.attributes[self.tgt_attr.id], 100)
        self.fit.character = None
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_other(self):
        # Here we check that self-reference modifies only carrier-item,
        # and nothing else is affected. We position item as character and
        # check character item to also check that items 'belonging' to self
        # are not affected too
        influence_source = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.character = influence_source
        influence_target = CharacterItem(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.character = None
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
