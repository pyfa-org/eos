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
from eos.const.eve import TypeCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestOperatorPenaltyImmuneCategory(CalculatorTestCase):
    """Test that several categories are immune to stacking penalty."""

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr(stackable=0)
        self.src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=self.src_attr.id)
        self.effect = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])

    def test_ship(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.ship,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=TypeCategoryId.ship,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.charge,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=TypeCategoryId.charge,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_skill(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.skill,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=TypeCategoryId.skill,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.subsystem,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=TypeCategoryId.subsystem,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_mixed(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.charge,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_with_not_immune(self):
        influence_src1 = Implant(self.mktype(
            category_id=TypeCategoryId.charge,
            attrs={self.src_attr.id: 50},
            effects=[self.effect]).id)
        influence_src2 = Implant(self.mktype(
            category_id=None,
            attrs={self.src_attr.id: 100},
            effects=[self.effect]).id)
        self.fit.implants.add(influence_src1)
        self.fit.implants.add(influence_src2)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 300)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
