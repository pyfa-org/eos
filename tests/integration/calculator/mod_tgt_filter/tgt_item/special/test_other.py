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


from eos import Charge
from eos import ModuleHigh
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestTgtItemSpecialOther(CalculatorTestCase):

    def make_modifier(self, src_attr_id, tgt_attr_id):
        return self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.other,
            tgt_attr_id=tgt_attr_id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr_id)

    def test_other_container(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.make_modifier(src_attr.id, tgt_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        influence_src = ModuleHigh(self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect]).id)
        self.fit.modules.high.append(influence_src)
        influence_tgt = Charge(self.mktype(attrs={tgt_attr.id: 100}).id)
        # Action
        influence_src.charge = influence_tgt
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 120)
        # Action
        # Manually remove target, then source, to make sure buffers are cleared
        # properly in this case
        influence_src.charge = None
        self.fit.modules.high.remove(influence_src)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_none_to_source(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier_container = self.make_modifier(src_attr.id, tgt_attr.id)
        effect_container = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_container])
        container = ModuleHigh(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=[effect_container]).id)
        modifier_charge = self.make_modifier(src_attr.id, tgt_attr.id)
        effect_charge = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_charge])
        charge = Charge(self.mktype(
            attrs={src_attr.id: 40, tgt_attr.id: 50},
            effects=[effect_charge]).id)
        self.fit.solar_system.source = None
        self.fit.modules.high.append(container)
        container.charge = charge
        # Action
        self.fit.solar_system.source = 'src1'
        # Verification
        self.assertAlmostEqual(container.attrs[tgt_attr.id], 140)
        self.assertAlmostEqual(charge.attrs[tgt_attr.id], 60)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_source_to_none(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier_container = self.make_modifier(src_attr.id, tgt_attr.id)
        effect_container = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_container])
        container = ModuleHigh(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=[effect_container]).id)
        modifier_charge = self.make_modifier(src_attr.id, tgt_attr.id)
        effect_charge = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_charge])
        charge = Charge(self.mktype(
            attrs={src_attr.id: 40, tgt_attr.id: 50},
            effects=[effect_charge]).id)
        self.fit.modules.high.append(container)
        container.charge = charge
        self.assertAlmostEqual(container.attrs[tgt_attr.id], 140)
        self.assertAlmostEqual(charge.attrs[tgt_attr.id], 60)
        # Action
        self.fit.solar_system.source = None
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
