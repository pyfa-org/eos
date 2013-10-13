#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.const.eos import State, Location, EffectBuildStatus, Context, FilterType, Operator
from eos.const.eve import EffectCategory, Operand
from eos.tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestModGangSrq(ModBuilderTestCase):
    """Test parsing of trees describing gang-mates' ship modules modification filtered by skill requirement"""

    def setUp(self):
        ModBuilderTestCase.setUp(self)
        e_tgt_srq = self.ef.make(1, operandID=Operand.def_type, expressionTypeID=3435)
        e_tgt_attr = self.ef.make(2, operandID=Operand.def_attr, expressionAttributeID=54)
        e_optr = self.ef.make(3, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(4, operandID=Operand.def_attr, expressionAttributeID=833)
        e_tgt_spec = self.ef.make(5, operandID=Operand.srq_attr, arg1=e_tgt_srq['expressionID'],
                                  arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(6, operandID=Operand.optr_tgt, arg1=e_optr['expressionID'],
                                  arg2=e_tgt_spec['expressionID'])
        self.e_add_mod = self.ef.make(7, operandID=Operand.add_gang_srq_mod, arg1=e_optr_tgt['expressionID'],
                                      arg2=e_src_attr['expressionID'])
        self.e_rm_mod = self.ef.make(8, operandID=Operand.rm_gang_srq_mod, arg1=e_optr_tgt['expressionID'],
                                     arg2=e_src_attr['expressionID'])

    def test_generic_build_success(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(modifier.source_attribute_id, 833)
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(modifier.target_attribute_id, 54)
        self.assertEqual(modifier.location, Location.ship)
        self.assertEqual(modifier.filter_type, FilterType.skill)
        self.assertEqual(modifier.filter_value, 3435)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_passive(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_active(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.active)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_target(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.target)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_eff_category_area(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.area)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_eff_category_online(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.online)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_overload(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.overload)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(len(self.log), 0)

    def test_eff_category_dungeon(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.dungeon)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_eff_category_system(self):
        modifiers, status = self.run_builder(self.e_add_mod['expressionID'],
                                             self.e_rm_mod['expressionID'],
                                             EffectCategory.system)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(len(self.log), 0)
