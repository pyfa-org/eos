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


from eos.const.eos import State, Domain, EffectBuildStatus, Scope, FilterType, Operator
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeModLocSrq(ModBuilderTestCase):
    """Test parsing of trees describing modification filtered by domain and skill requirement"""

    def setUp(self):
        super().setUp()
        e_tgt_loc = self.ef.make(1, operandID=Operand.def_loc, expressionValue='Ship')
        e_tgt_srq = self.ef.make(2, operandID=Operand.def_type, expressionTypeID=3307)
        e_tgt_attr = self.ef.make(3, operandID=Operand.def_attr, expressionAttributeID=54)
        e_optr = self.ef.make(4, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(5, operandID=Operand.def_attr, expressionAttributeID=491)
        e_tgt_itms = self.ef.make(
            6, operandID=Operand.loc_srq,
            arg1=e_tgt_loc['expressionID'],
            arg2=e_tgt_srq['expressionID']
        )
        e_tgt_spec = self.ef.make(
            7, operandID=Operand.itm_attr,
            arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            8, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        self.e_add_mod = self.ef.make(
            9, operandID=Operand.add_loc_srq_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        self.e_rm_mod = self.ef.make(
            10, operandID=Operand.rm_loc_srq_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )

    def test_generic_build_success(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(modifier.src_attr, 491)
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(modifier.tgt_attr, 54)
        self.assertEqual(modifier.domain, Domain.ship)
        self.assertEqual(modifier.filter_type, FilterType.skill)
        self.assertEqual(modifier.filter_value, 3307)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_passive(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_active(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.active
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_target(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.target
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.scope, Scope.projected)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_area(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.area
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_eff_category_online(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.online
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_overload(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.overload
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_dungeon(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.dungeon
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_eff_category_system(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.system
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(len(self.log), 0)
