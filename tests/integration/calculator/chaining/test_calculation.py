# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from eos import Implant
from eos import Rig
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestCalculationChain(CalculatorTestCase):
    """Check that calculation process uses modified attributes."""

    def test_calculation(self):
        attr1 = self.mkattr()
        attr2 = self.mkattr()
        attr3 = self.mkattr()
        attr4 = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=attr2.id,
            operator=ModOperator.post_mul,
            src_attr_id=attr1.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier1])
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=attr3.id,
            operator=ModOperator.post_percent,
            src_attr_id=attr2.id)
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier2])
        modifier3 = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=attr4.id,
            operator=ModOperator.post_percent,
            src_attr_id=attr3.id)
        effect3 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier3])
        implant = Implant(self.mktype(
            attrs={attr1.id: 5, attr2.id: 20}, effects=(effect1, effect2)).id)
        ship = Ship(self.mktype(attrs={attr3.id: 150}, effects=[effect3]).id)
        rig = Rig(self.mktype(attrs={attr4.id: 12.5}).id)
        self.fit.implants.add(implant)
        self.fit.ship = ship
        # Action
        self.fit.rigs.add(rig)
        # Verification
        # If everything is processed properly, item1 will multiply attr2 by
        # attr1 on self, resulting in 20 * 5 = 100, then apply it as percentage
        # modifier on ship's (item2) attr3, resulting in 150 + 100% = 300, then
        # it is applied to all entities assigned to ship, including item3, to
        # theirs attr4 as percentage modifier again - so final result is 12.5 +
        # 300% = 50
        self.assertAlmostEqual(rig.attrs[attr4.id], 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
