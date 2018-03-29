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


from eos import Character
from eos import Charge
from eos import ModuleHigh
from eos import ModuleLow
from eos import Rig
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import TypeGroupId
from eos.const.eve import TypeId
from tests.integration.customization.testcase import CustomizationTestCase


class TestMissileDmg(CustomizationTestCase):

    def setUp(self):
        CustomizationTestCase.setUp(self)
        # Create character
        self.mkattr(attr_id=AttrId.missile_dmg_mult)
        self.fit.character = Character(self.mktype(
            type_id=TypeId.character_static,
            group_id=TypeGroupId.character,
            attrs={AttrId.missile_dmg_mult: 1}).id)
        # Create Ballistic Control System item
        bcs_src_attr = self.mkattr()
        bcs_mod = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.character,
            tgt_attr_id=AttrId.missile_dmg_mult,
            operator=ModOperator.post_percent,
            src_attr_id=bcs_src_attr.id)
        bcs_effect = self.mkeffect(
            category_id=EffectCategoryId.online,
            modifiers=[bcs_mod])
        online_effect = self.mkeffect(
            effect_id=EffectId.online,
            category_id=EffectCategoryId.active)
        bcs_type = self.mktype(
            attrs={bcs_src_attr.id: 10},
            effects=[bcs_effect, online_effect])
        bcs = ModuleLow(bcs_type.id, state=State.online)
        self.fit.modules.low.append(bcs)
        # Create launcher
        self.launcher = ModuleHigh(self.mktype())
        self.fit.modules.high.append(self.launcher)

    def make_charge(self, attr_id):
        self.mkattr(attr_id)
        return Charge(self.mktype(attrs={
            attr_id: 100,
            AttrId.required_skill_1: TypeId.missile_launcher_operation,
            AttrId.required_skill_1_level: 1}).id)

    def test_charge_attr_em(self):
        charge = self.make_charge(AttrId.em_dmg)
        self.launcher.charge = charge
        # Verification
        self.assertAlmostEqual(charge.attrs[AttrId.em_dmg], 110)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_attr_therm(self):
        charge = self.make_charge(AttrId.therm_dmg)
        self.launcher.charge = charge
        # Verification
        self.assertAlmostEqual(charge.attrs[AttrId.therm_dmg], 110)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_attr_kin(self):
        charge = self.make_charge(AttrId.kin_dmg)
        self.launcher.charge = charge
        # Verification
        self.assertAlmostEqual(charge.attrs[AttrId.kin_dmg], 110)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_attr_expl(self):
        charge = self.make_charge(AttrId.expl_dmg)
        self.launcher.charge = charge
        # Verification
        self.assertAlmostEqual(charge.attrs[AttrId.expl_dmg], 110)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_skillrq_absent(self):
        self.mkattr(AttrId.em_dmg)
        charge = Charge(self.mktype(attrs={AttrId.em_dmg: 100}).id)
        self.launcher.charge = charge
        # Verification
        self.assertAlmostEqual(charge.attrs[AttrId.em_dmg], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_other_class(self):
        self.mkattr(AttrId.em_dmg)
        item = Rig(self.mktype(attrs={
            AttrId.em_dmg: 100,
            AttrId.required_skill_1: TypeId.missile_launcher_operation,
            AttrId.required_skill_1_level: 1}).id)
        self.fit.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[AttrId.em_dmg], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
