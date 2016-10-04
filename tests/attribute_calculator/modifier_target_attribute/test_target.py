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


class TestTargetAttribute(AttrCalcTestCase):
    """Test that only targeted attributes are modified"""

    def test_target_attributes(self):
        tgt_attr1 = self.ch.attribute(attribute_id=1)
        tgt_attr2 = self.ch.attribute(attribute_id=2)
        tgt_attr3 = self.ch.attribute(attribute_id=3)
        src_attr = self.ch.attribute(attribute_id=4)
        modifier1 = Modifier()
        modifier1.state = State.offline
        modifier1.scope = Scope.local
        modifier1.src_attr = src_attr.id
        modifier1.operator = Operator.post_percent
        modifier1.tgt_attr = tgt_attr1.id
        modifier1.domain = Domain.self_
        modifier1.filter_type = None
        modifier1.filter_value = None
        modifier2 = Modifier()
        modifier2.state = State.offline
        modifier2.scope = Scope.local
        modifier2.src_attr = src_attr.id
        modifier2.operator = Operator.post_percent
        modifier2.tgt_attr = tgt_attr2.id
        modifier2.domain = Domain.self_
        modifier2.filter_type = None
        modifier2.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier1, modifier2)
        holder = IndependentItem(self.ch.type_(
            type_id=1, effects=(effect,),
            attributes={tgt_attr1.id: 50, tgt_attr2.id: 80, tgt_attr3.id: 100, src_attr.id: 20}
        ))
        self.fit.items.add(holder)
        # First attribute should be modified by modifier1
        self.assertAlmostEqual(holder.attributes[tgt_attr1.id], 60)
        # Second should be modified by modifier2
        self.assertAlmostEqual(holder.attributes[tgt_attr2.id], 96)
        # Third should stay unmodified
        self.assertAlmostEqual(holder.attributes[tgt_attr3.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
