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


from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator, State
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestModItemDomainUnknown(CalculatorTestCase):
    """Test reaction to unknown domain specification for direct modification"""

    def test_combination(self):
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        invalid_modifier = DogmaModifier()
        invalid_modifier.type = ModifierTargetFilter.item
        invalid_modifier.domain = 1972
        invalid_modifier.state = State.offline
        invalid_modifier.src_attr = src_attr.id
        invalid_modifier.operator = ModifierOperator.post_percent
        invalid_modifier.tgt_attr = tgt_attr.id
        valid_modifier = DogmaModifier()
        valid_modifier.type = ModifierTargetFilter.item
        valid_modifier.domain = ModifierDomain.self
        valid_modifier.state = State.offline
        valid_modifier.src_attr = src_attr.id
        valid_modifier.operator = ModifierOperator.post_percent
        valid_modifier.tgt_attr = tgt_attr.id
        effect = self.ch.effect(
            effect_id=1, category=EffectCategory.passive,
            modifiers=(invalid_modifier, valid_modifier)
        )
        item = IndependentItem(self.ch.type(
            type_id=1, effects=(effect,),
            attributes={src_attr.id: 20, tgt_attr.id: 100}
        ))
        # Action
        self.fit.items.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
