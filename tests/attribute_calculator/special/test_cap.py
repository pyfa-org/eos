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


class TestCap(AttrCalcTestCase):
    """Test how capped attribute values are processed"""

    def setUp(self):
        super().setUp()
        self.capped_attr = self.ch.attribute(attribute_id=1, max_attribute=2)
        self.capping_attr = self.ch.attribute(attribute_id=2, default_value=5)
        self.source_attr = self.ch.attribute(attribute_id=3)
        # Just to make sure cap is applied to final value, not
        # base, make some basic modification modifier
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.source_attr.id
        modifier.operator = Operator.post_mul
        modifier.tgt_attr = self.capped_attr.id
        modifier.domain = Domain.self_
        modifier.filter_type = None
        modifier.filter_value = None
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_cap_default(self):
        # Check that cap is applied properly when holder
        # doesn't have base value of capping attribute
        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,),
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6}
        ))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[self.capped_attr.id], 5)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_cap_original(self):
        # Make sure that holder's own specified attribute
        # value is taken as cap
        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,),
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6, self.capping_attr.id: 2}
        ))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[self.capped_attr.id], 2)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_cap_modified(self):
        # Make sure that holder's own specified attribute
        # value is taken as cap, and it's taken with all
        # modifications applied onto it
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.source_attr.id
        modifier.operator = Operator.post_mul
        modifier.tgt_attr = self.capping_attr.id
        modifier.domain = Domain.self_
        modifier.filter_type = None
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=2, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect, effect),
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6, self.capping_attr.id: 0.1}
        ))
        self.fit.items.add(holder)
        # Attr value is 3 * 6 = 18, but cap value is 0.1 * 6 = 0.6
        self.assertAlmostEqual(holder.attributes[self.capped_attr.id], 0.6)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_cap_update(self):
        # If cap updates, capped attributes should
        # be updated too
        holder = ShipItem(self.ch.type_(
            type_id=1, effects=(self.effect,),
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6, self.capping_attr.id: 2}
        ))
        self.fit.items.add(holder)
        # Check attribute vs original cap
        self.assertAlmostEqual(holder.attributes[self.capped_attr.id], 2)
        # Add something which changes capping attribute
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.source_attr.id
        modifier.operator = Operator.post_mul
        modifier.tgt_attr = self.capping_attr.id
        modifier.domain = Domain.ship
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=2, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        cap_updater = IndependentItem(self.ch.type_(
            type_id=2, effects=(effect,),
            attributes={self.source_attr.id: 3.5}
        ))
        self.fit.items.add(cap_updater)
        # As capping attribute is updated, capped attribute must be updated too
        self.assertAlmostEqual(holder.attributes[self.capped_attr.id], 7)
        self.fit.items.remove(holder)
        self.fit.items.remove(cap_updater)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
