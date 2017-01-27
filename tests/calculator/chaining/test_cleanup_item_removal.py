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


from eos.const.eos import ModifierType, ModifierDomain, ModifierOperator, State
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, CharacterItem, ShipItem


class TestCleanupChainRemoval(CalculatorTestCase):
    """Check that removed item damages all attributes which were relying on its attributes"""

    def test_attribute(self):
        # Setup
        attr1 = self.ch.attribute(attribute_id=1)
        attr2 = self.ch.attribute(attribute_id=2)
        attr3 = self.ch.attribute(attribute_id=3)
        modifier1 = Modifier()
        modifier1.type = ModifierType.item
        modifier1.domain = ModifierDomain.ship
        modifier1.state = State.offline
        modifier1.src_attr = attr1.id
        modifier1.operator = ModifierOperator.post_mul
        modifier1.tgt_attr = attr2.id
        effect1 = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect1.modifiers = (modifier1,)
        item1 = CharacterItem(self.ch.type(type_id=1, effects=(effect1,), attributes={attr1.id: 5}))
        modifier2 = Modifier()
        modifier2.type = ModifierType.domain
        modifier2.state = State.offline
        modifier2.src_attr = attr2.id
        modifier2.operator = ModifierOperator.post_percent
        modifier2.tgt_attr = attr3.id
        modifier2.domain = ModifierDomain.ship
        effect2 = self.ch.effect(effect_id=2, category=EffectCategory.passive)
        effect2.modifiers = (modifier2,)
        item2 = IndependentItem(self.ch.type(type_id=2, effects=(effect2,), attributes={attr2.id: 7.5}))
        item3 = ShipItem(self.ch.type(type_id=3, attributes={attr3.id: 0.5}))
        self.fit.items.add(item1)
        self.fit.ship = item2
        self.fit.items.add(item3)
        self.assertAlmostEqual(item3.attributes[attr3.id], 0.6875)
        # Action
        self.fit.items.remove(item1)
        # Checks
        # When item1 is removed, attr2 of item2 and attr3 of item3
        # must be cleaned to allow recalculation of attr3 based on new data
        self.assertAlmostEqual(item3.attributes[attr3.id], 0.5375)
        # Misc
        self.fit.ship = None
        self.fit.items.remove(item3)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
