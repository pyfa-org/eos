# ==============================================================================
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
# ==============================================================================


from eos import *
from eos.const.eos import ModDomain, ModOperator, ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestCleanupChainRemoval(CalculatorTestCase):
    """Check that removed item "damages" all neccessary attribute values."""

    def test_attr(self):
        # Setup
        attr1 = self.mkattr()
        attr2 = self.mkattr()
        attr3 = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=attr2.id,
            operator=ModOperator.post_mul,
            src_attr_id=attr1.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier1])
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=attr3.id,
            operator=ModOperator.post_percent,
            src_attr_id=attr2.id)
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier2])
        implant = Implant(self.mktype(
            attrs={attr1.id: 5}, effects=[effect1]).id)
        ship = Ship(self.mktype(attrs={attr2.id: 7.5}, effects=[effect2]).id)
        rig = Rig(self.mktype(attrs={attr3.id: 0.5}).id)
        self.fit.implants.add(implant)
        self.fit.ship = ship
        self.fit.rigs.add(rig)
        self.assertAlmostEqual(rig.attrs[attr3.id], 0.6875)
        # Action
        self.fit.implants.remove(implant)
        # Verification
        # When item1 is removed, attr2 of item2 and attr3 of item3 must be
        # cleaned to allow recalculation of attr3 based on new data
        self.assertAlmostEqual(rig.attrs[attr3.id], 0.5375)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
