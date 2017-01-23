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


from eos.const.eos import State, ModifierType, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, CharacterItem, ShipItem


class TestCalculationChain(CalculatorTestCase):
    """Check that calculation process uses modified attributes as data source"""

    def test_calculation(self):
        attr1 = self.ch.attribute(attribute_id=1)
        attr2 = self.ch.attribute(attribute_id=2)
        attr3 = self.ch.attribute(attribute_id=3)
        attr4 = self.ch.attribute(attribute_id=4)
        modifier1 = Modifier()
        modifier1.type = ModifierType.item
        modifier1.domain = ModifierDomain.self
        modifier1.state = State.offline
        modifier1.src_attr = attr1.id
        modifier1.operator = ModifierOperator.post_mul
        modifier1.tgt_attr = attr2.id
        effect1 = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect1.modifiers = (modifier1,)
        modifier2 = Modifier()
        modifier2.type = ModifierType.item
        modifier2.domain = ModifierDomain.ship
        modifier2.state = State.offline
        modifier2.src_attr = attr2.id
        modifier2.operator = ModifierOperator.post_percent
        modifier2.tgt_attr = attr3.id
        effect2 = self.ch.effect(effect_id=2, category=EffectCategory.passive)
        effect2.modifiers = (modifier2,)
        holder1 = CharacterItem(
            self.ch.type_(type_id=1, effects=(effect1, effect2),
            attributes={attr1.id: 5, attr2.id: 20})
        )
        modifier3 = Modifier()
        modifier3.type = ModifierType.domain
        modifier3.domain = ModifierDomain.ship
        modifier3.state = State.offline
        modifier3.src_attr = attr3.id
        modifier3.operator = ModifierOperator.post_percent
        modifier3.tgt_attr = attr4.id
        effect3 = self.ch.effect(effect_id=3, category=EffectCategory.passive)
        effect3.modifiers = (modifier3,)
        holder2 = IndependentItem(self.ch.type_(type_id=2, effects=(effect3,), attributes={attr3.id: 150}))
        holder3 = ShipItem(self.ch.type_(type_id=3, attributes={attr4.id: 12.5}))
        self.fit.items.add(holder1)
        self.fit.ship = holder2
        self.fit.items.add(holder3)
        # If everything is processed properly, holder1 will multiply attr2 by attr1
        # on self, resulting in 20 * 5 = 100, then apply it as percentage modifier
        # on ship's (holder2) attr3, resulting in 150 + 100% = 300, then it is applied
        # to all entities assigned to ship, including holder3, to theirs attr4 as
        # percentage modifier again - so final result is 12.5 + 300% = 50
        self.assertAlmostEqual(holder3.attributes[attr4.id], 50)
        self.fit.items.remove(holder1)
        self.fit.ship = None
        self.fit.items.remove(holder3)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
