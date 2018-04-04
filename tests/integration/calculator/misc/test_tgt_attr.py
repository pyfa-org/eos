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


from eos import Rig
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestTgtAttr(CalculatorTestCase):

    def test_tgt_attrs(self):
        tgt_attr1 = self.mkattr()
        tgt_attr2 = self.mkattr()
        tgt_attr3 = self.mkattr()
        src_attr = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr1.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr2.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=(modifier1, modifier2))
        item = Rig(self.mktype(
            attrs={
                tgt_attr1.id: 50, tgt_attr2.id: 80,
                tgt_attr3.id: 100, src_attr.id: 20},
            effects=[effect]).id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        # First attribute should be modified by modifier1
        self.assertAlmostEqual(item.attrs[tgt_attr1.id], 60)
        # Second should be modified by modifier2
        self.assertAlmostEqual(item.attrs[tgt_attr2.id], 96)
        # Third should stay unmodified
        self.assertAlmostEqual(item.attrs[tgt_attr3.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
