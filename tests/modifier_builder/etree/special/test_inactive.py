# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeInactive(ModBuilderTestCase):
    """Test parsing of trees involving disabled operands"""

    def setUp(self):
        super().setUp()
        self.stub = self.ef.make(-1, operandID=Operand.def_int, expressionValue='1')

    def test_attack(self):
        disabled_pre = self.ef.make(1, operandID=Operand.attack)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_cargo_scan(self):
        disabled_pre = self.ef.make(1, operandID=Operand.cargo_scan)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_cheat_tele_dock(self):
        disabled_pre = self.ef.make(1, operandID=Operand.cheat_tele_dock)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_cheat_tele_gate(self):
        disabled_pre = self.ef.make(1, operandID=Operand.cheat_tele_gate)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_aoe_decloak(self):
        disabled_pre = self.ef.make(1, operandID=Operand.aoe_decloak)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_ecm_burst(self):
        disabled_pre = self.ef.make(1, operandID=Operand.ecm_burst)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_aoe_dmg(self):
        disabled_pre = self.ef.make(1, operandID=Operand.aoe_dmg)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_missile_launch(self):
        disabled_pre = self.ef.make(1, operandID=Operand.missile_launch)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_defender_launch(self):
        disabled_pre = self.ef.make(1, operandID=Operand.defender_launch)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_fof_launch(self):
        disabled_pre = self.ef.make(1, operandID=Operand.fof_launch)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_mine(self):
        disabled_pre = self.ef.make(1, operandID=Operand.mine)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_power_booster(self):
        disabled_pre = self.ef.make(1, operandID=Operand.power_booster)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_ship_scan(self):
        disabled_pre = self.ef.make(1, operandID=Operand.ship_scan)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_survey_scan(self):
        disabled_pre = self.ef.make(1, operandID=Operand.survey_scan)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_tgt_hostile(self):
        disabled_pre = self.ef.make(1, operandID=Operand.tgt_hostile)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_tgt_silent(self):
        disabled_pre = self.ef.make(1, operandID=Operand.tgt_silent)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_tool_tgt_skills(self):
        disabled_pre = self.ef.make(1, operandID=Operand.tool_tgt_skills)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_user_error(self):
        disabled_pre = self.ef.make(1, operandID=Operand.user_error)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def test_vrf_tgt_grp(self):
        disabled_pre = self.ef.make(1, operandID=Operand.vrf_tgt_grp)
        effect_row = {
            'pre_expression': disabled_pre['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)
