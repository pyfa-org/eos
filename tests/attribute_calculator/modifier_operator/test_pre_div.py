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
from tests.attribute_calculator.environment import IndependentItem, ShipItem


class TestOperatorPreDiv(AttrCalcTestCase):
    """Test pre-division operator"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = src_attr.id
        modifier.operator = Operator.post_div
        modifier.tgt_attr = self.tgt_attr.id
        modifier.domain = Domain.ship
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        self.influence_source1 = IndependentItem(self.ch.type_(
            type_id=1, effects=(effect,), attributes={src_attr.id: 1.2}))
        self.influence_source2 = IndependentItem(self.ch.type_(
            type_id=2, effects=(effect,), attributes={src_attr.id: 1.5}))
        self.influence_source3 = IndependentItem(self.ch.type_(
            type_id=3, effects=(effect,), attributes={src_attr.id: 0.1}))
        self.influence_source4 = IndependentItem(self.ch.type_(
            type_id=4, effects=(effect,), attributes={src_attr.id: 0.75}))
        self.influence_source5 = IndependentItem(self.ch.type_(
            type_id=5, effects=(effect,), attributes={src_attr.id: 5}))
        self.influence_target = ShipItem(self.ch.type_(type_id=6, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(self.influence_source1)
        self.fit.items.add(self.influence_source2)
        self.fit.items.add(self.influence_source3)
        self.fit.items.add(self.influence_source4)
        self.fit.items.add(self.influence_source5)
        self.fit.items.add(self.influence_target)

    def test_unpenalized(self):
        self.tgt_attr.stackable = True
        self.assertAlmostEqual(self.influence_target.attributes[self.tgt_attr.id], 148.1481481)
        self.fit.items.remove(self.influence_source1)
        self.fit.items.remove(self.influence_source2)
        self.fit.items.remove(self.influence_source3)
        self.fit.items.remove(self.influence_source4)
        self.fit.items.remove(self.influence_source5)
        self.fit.items.remove(self.influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_penalized(self):
        self.tgt_attr.stackable = False
        self.assertAlmostEqual(self.influence_target.attributes[self.tgt_attr.id], 165.7908726)
        self.fit.items.remove(self.influence_source1)
        self.fit.items.remove(self.influence_source2)
        self.fit.items.remove(self.influence_source3)
        self.fit.items.remove(self.influence_source4)
        self.fit.items.remove(self.influence_source5)
        self.fit.items.remove(self.influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
