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
from eos.const.eve import Attribute, EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem


class TestRounding(AttrCalcTestCase):

    def test_cpu_down(self):
        attr = self.ch.attribute(attribute_id=Attribute.cpu)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 2.3333}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[attr.id], 2.33)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_cpu_up(self):
        attr = self.ch.attribute(attribute_id=Attribute.cpu)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 2.6666}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[attr.id], 2.67)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_cpu_modified(self):
        src_attr = self.ch.attribute(attribute_id=1)
        tgt_attr = self.ch.attribute(attribute_id=Attribute.cpu)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = tgt_attr.id
        modifier.domain = Domain.self_
        modifier.filter_type = None
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)

        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(effect,),
            attributes={src_attr.id: 20, tgt_attr.id: 1.9444}
        ))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[tgt_attr.id], 2.33)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_cpu_output(self):
        attr = self.ch.attribute(attribute_id=Attribute.cpu_output)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 2.6666}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[attr.id], 2.67)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_power(self):
        attr = self.ch.attribute(attribute_id=Attribute.power)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 2.6666}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[attr.id], 2.67)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_power_output(self):
        attr = self.ch.attribute(attribute_id=Attribute.power_output)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 2.6666}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[attr.id], 2.67)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_other(self):
        attr = self.ch.attribute(attribute_id=1008)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 2.6666}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[attr.id], 2.6666)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
