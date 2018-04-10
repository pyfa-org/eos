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
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestTgtItemSpecialAwaitingShip(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.influence_src = Implant(self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect]).id)
        self.influence_tgt = Ship(self.mktype(
            attrs={self.tgt_attr.id: 100}).id)

    def test_manual(self):
        self.fit.implants.add(self.influence_src)
        # Action
        # Here we add influence target after adding source, to make sure
        # modifiers wait for target to appear, and then are applied onto it
        self.fit.ship = self.influence_tgt
        # Verification
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 120)
        # Action
        # Manually remove target, then source, to make sure buffers are cleared
        # properly in this case
        self.fit.ship = None
        self.fit.implants.remove(self.influence_src)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_to_source(self):
        self.fit.solar_system.source = None
        self.fit.implants.add(self.influence_src)
        self.fit.ship = self.influence_tgt
        # Action
        self.fit.solar_system.source = 'src1'
        # Verification
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_source_to_none(self):
        self.fit.implants.add(self.influence_src)
        self.fit.ship = self.influence_tgt
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 120)
        # Action
        self.fit.solar_system.source = None
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
