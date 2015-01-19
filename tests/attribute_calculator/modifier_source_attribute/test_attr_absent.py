#===============================================================================
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
#===============================================================================


from eos.const.eos import State, Location, Context, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from eos.tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from eos.tests.attribute_calculator.environment import IndependentItem
from eos.tests.environment import Logger


class TestSourceAttrAbsent(AttrCalcTestCase):
    """Test how calculator reacts to source attribute which is absent"""

    def test_combination(self):
        tgt_attr = self.ch.attribute(attribute_id=1)
        abs_attr = self.ch.attribute(attribute_id=2)
        src_attr = self.ch.attribute(attribute_id=3)
        invalid_modifier = Modifier()
        invalid_modifier.state = State.offline
        invalid_modifier.context = Context.local
        invalid_modifier.source_attribute_id = abs_attr.id
        invalid_modifier.operator = Operator.post_percent
        invalid_modifier.target_attribute_id = tgt_attr.id
        invalid_modifier.location = Location.self_
        invalid_modifier.filter_type = None
        invalid_modifier.filter_value = None
        valid_modifier = Modifier()
        valid_modifier.state = State.offline
        valid_modifier.context = Context.local
        valid_modifier.source_attribute_id = src_attr.id
        valid_modifier.operator = Operator.post_mul
        valid_modifier.target_attribute_id = tgt_attr.id
        valid_modifier.location = Location.self_
        valid_modifier.filter_type = None
        valid_modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category_id=EffectCategory.passive)
        effect.modifiers = (invalid_modifier, valid_modifier)
        holder = IndependentItem(self.ch.type_(type_id=1, effects=(effect,),
                                               attributes={src_attr.id: 1.5, tgt_attr.id: 100}))
        self.fit.items.add(holder)
        # Invalid source value shouldn't screw whole calculation process
        self.assertNotAlmostEqual(holder.attributes[tgt_attr.id], 100)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.attribute_calculator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, 'unable to find base value for attribute 2 on item 1')
        self.fit.items.remove(holder)
        self.assert_link_buffers_empty(self.fit)
