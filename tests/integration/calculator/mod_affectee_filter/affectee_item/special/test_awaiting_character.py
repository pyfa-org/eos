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


from eos import Character
from eos import Implant
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModAffecteeFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestAffecteeItemSpecialAwaitingChar(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.character,
            affectee_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.influence_src = Implant(self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect]).id)
        self.influence_tgt = Character(self.mktype(
            attrs={self.tgt_attr.id: 100}).id)

    def test_manual(self):
        self.fit.implants.add(self.influence_src)
        # Action
        # Here we add influence target after adding source, to make sure
        # modifiers wait for target to appear, and then are applied onto it
        self.fit.character = self.influence_tgt
        # Verification
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 120)
        # Action
        # Manually remove target, then source, to make sure buffers are cleared
        # properly in this case
        self.fit.character = None
        self.fit.implants.remove(self.influence_src)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_source_to_none(self):
        self.fit.implants.add(self.influence_src)
        self.fit.character = self.influence_tgt
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 120)
        # Action
        self.fit.solar_system.source = None
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_none_to_source(self):
        self.fit.solar_system.source = None
        self.fit.implants.add(self.influence_src)
        self.fit.character = self.influence_tgt
        # Action
        self.fit.solar_system.source = 'src1'
        # Verification
        self.assertAlmostEqual(self.influence_tgt.attrs[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
