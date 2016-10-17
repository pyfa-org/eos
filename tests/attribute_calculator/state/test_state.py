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
from tests.attribute_calculator.environment import IndependentItem


class TestStateSwitching(AttrCalcTestCase):
    """Test holder state switching and modifier states"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1, stackable=1)
        src_attr1 = self.ch.attribute(attribute_id=2)
        src_attr2 = self.ch.attribute(attribute_id=3)
        src_attr3 = self.ch.attribute(attribute_id=4)
        src_attr4 = self.ch.attribute(attribute_id=5)
        modifier_off = Modifier()
        modifier_off.state = State.offline
        modifier_off.scope = Scope.local
        modifier_off.src_attr = src_attr1.id
        modifier_off.operator = Operator.post_mul
        modifier_off.tgt_attr = self.tgt_attr.id
        modifier_off.domain = Domain.self_
        modifier_off.filter_type = None
        modifier_off.filter_value = None
        modifier_on = Modifier()
        modifier_on.state = State.online
        modifier_on.scope = Scope.local
        modifier_on.src_attr = src_attr2.id
        modifier_on.operator = Operator.post_mul
        modifier_on.tgt_attr = self.tgt_attr.id
        modifier_on.domain = Domain.self_
        modifier_on.filter_type = None
        modifier_on.filter_value = None
        modifier_act = Modifier()
        modifier_act.state = State.active
        modifier_act.scope = Scope.local
        modifier_act.src_attr = src_attr3.id
        modifier_act.operator = Operator.post_mul
        modifier_act.tgt_attr = self.tgt_attr.id
        modifier_act.domain = Domain.self_
        modifier_act.filter_type = None
        modifier_act.filter_value = None
        modifier_over = Modifier()
        modifier_over.state = State.overload
        modifier_over.scope = Scope.local
        modifier_over.src_attr = src_attr4.id
        modifier_over.operator = Operator.post_mul
        modifier_over.tgt_attr = self.tgt_attr.id
        modifier_over.domain = Domain.self_
        modifier_over.filter_type = None
        modifier_over.filter_value = None
        # Overload category will make sure that holder can enter all states
        effect = self.ch.effect(effect_id=1, category=EffectCategory.overload)
        effect.modifiers = (modifier_off, modifier_on, modifier_act, modifier_over)
        self.holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(effect,),
            attributes={
                self.tgt_attr.id: 100, src_attr1.id: 1.1, src_attr2.id: 1.3,
                src_attr3.id: 1.5, src_attr4.id: 1.7
            }
        ))

    def test_fit_offline(self):
        self.holder.state = State.offline
        self.fit.items.add(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 110)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_fit_online(self):
        self.holder.state = State.online
        self.fit.items.add(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 143)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_fit_active(self):
        self.holder.state = State.active
        self.fit.items.add(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 214.5)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_fit_overloaded(self):
        self.holder.state = State.overload
        self.fit.items.add(self.holder)
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 364.65)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_switch_up_single(self):
        self.holder.state = State.offline
        self.fit.items.add(self.holder)
        self.holder.state = State.online
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 143)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_switch_up_multiple(self):
        self.holder.state = State.online
        self.fit.items.add(self.holder)
        self.holder.state = State.overload
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 364.65)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_switch_down_single(self):
        self.holder.state = State.overload
        self.fit.items.add(self.holder)
        self.holder.state = State.active
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 214.5)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_switch_down_multiple(self):
        self.holder.state = State.active
        self.fit.items.add(self.holder)
        self.holder.state = State.offline
        self.assertAlmostEqual(self.holder.attributes[self.tgt_attr.id], 110)
        self.fit.items.remove(self.holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
