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


from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestTargetAttribute(CalculatorTestCase):
    """Test that only targeted attributes are modified"""

    def test_target_attributes(self):
        tgt_attr1 = self.ch.attribute(attribute_id=1)
        tgt_attr2 = self.ch.attribute(attribute_id=2)
        tgt_attr3 = self.ch.attribute(attribute_id=3)
        src_attr = self.ch.attribute(attribute_id=4)
        modifier1 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr1.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        modifier2 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr2.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier1, modifier2)
        item = IndependentItem(self.ch.type(
            type_id=1, effects=(effect,),
            attributes={tgt_attr1.id: 50, tgt_attr2.id: 80, tgt_attr3.id: 100, src_attr.id: 20}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        # First attribute should be modified by modifier1
        self.assertAlmostEqual(item.attributes[tgt_attr1.id], 60)
        # Second should be modified by modifier2
        self.assertAlmostEqual(item.attributes[tgt_attr2.id], 96)
        # Third should stay unmodified
        self.assertAlmostEqual(item.attributes[tgt_attr3.id], 100)
        # Cleanup
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
