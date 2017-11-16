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


class TestTgtDomainDomainTgt(CalculatorTestCase):

    def test_no_effect(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.target,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        influence_src = Implant(self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect]).id)
        influence_tgt = Rig(self.mktype(attrs={tgt_attr.id: 100}).id)
        self.fit.rigs.add(influence_tgt)
        # Action
        self.fit.implants.add(influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
