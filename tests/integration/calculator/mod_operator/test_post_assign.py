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
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestOperatorPostAssign(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_assign,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        self.influence_src1 = Implant(self.mktype(
            attrs={src_attr.id: 10}, effects=[effect]).id)
        self.influence_src2 = Implant(self.mktype(
            attrs={src_attr.id: -20}, effects=[effect]).id)
        self.influence_src3 = Implant(self.mktype(
            attrs={src_attr.id: 53}, effects=[effect]).id)
        self.influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(self.influence_src1)
        self.fit.implants.add(self.influence_src2)
        self.fit.implants.add(self.influence_src3)
        self.fit.rigs.add(self.influence_tgt)

    def test_high_good(self):
        self.tgt_attr.high_is_good = True
        # Verification
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 53)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_high_bad(self):
        self.tgt_attr.high_is_good = False
        # Verification
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], -20)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
