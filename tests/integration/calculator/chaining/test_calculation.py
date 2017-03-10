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


from eos import *
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestCalculationChain(CalculatorTestCase):
    """Check that calculation process uses modified attributes as data source"""

    def test_calculation(self):
        attr1 = self.ch.attribute()
        attr2 = self.ch.attribute()
        attr3 = self.ch.attribute()
        attr4 = self.ch.attribute()
        modifier1 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=attr2.id,
            operator=ModifierOperator.post_mul,
            src_attr=attr1.id
        )
        effect1 = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier1,))
        modifier2 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=attr3.id,
            operator=ModifierOperator.post_percent,
            src_attr=attr2.id
        )
        effect2 = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier2,))
        modifier3 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=attr4.id,
            operator=ModifierOperator.post_percent,
            src_attr=attr3.id
        )
        effect3 = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier3,))
        implant_item = Implant(self.ch.type(effects=(effect1, effect2), attributes={attr1.id: 5, attr2.id: 20}).id)
        ship_item = Ship(self.ch.type(effects=(effect3,), attributes={attr3.id: 150}).id)
        rig_item = Rig(self.ch.type(attributes={attr4.id: 12.5}).id)
        self.fit.implants.add(implant_item)
        self.fit.ship = ship_item
        # Action
        self.fit.rigs.add(rig_item)
        # Verification
        # If everything is processed properly, item1 will multiply attr2 by attr1
        # on self, resulting in 20 * 5 = 100, then apply it as percentage modifier
        # on ship's (item2) attr3, resulting in 150 + 100% = 300, then it is applied
        # to all entities assigned to ship, including item3, to theirs attr4 as
        # percentage modifier again - so final result is 12.5 + 300% = 50
        self.assertAlmostEqual(rig_item.attributes[attr4.id], 50)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
