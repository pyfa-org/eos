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


from eos.const.eos import (
    EffectBuildStatus, ModifierDomain, ModifierOperator, ModifierTargetFilter)
from eos.const.eve import OperandId
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeTgtOwnSrq(ModBuilderTestCase):

    def make_etree(self, domain):
        e_tgt_own = self.ef.make(
            1, operandID=OperandId.def_dom, expressionValue=domain)
        e_tgt_srq = self.ef.make(
            2, operandID=OperandId.def_type, expressionTypeID=3412)
        e_tgt_attr = self.ef.make(
            3, operandID=OperandId.def_attr, expressionAttributeID=1372)
        e_optr = self.ef.make(
            4, operandID=OperandId.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(
            5, operandID=OperandId.def_attr, expressionAttributeID=1156)
        e_tgt_itms = self.ef.make(
            6, operandID=OperandId.dom_srq, arg1=e_tgt_own['expressionID'],
            arg2=e_tgt_srq['expressionID'])
        e_tgt_spec = self.ef.make(
            7, operandID=OperandId.itm_attr, arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(
            8, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID'])
        e_add_mod = self.ef.make(
            9, operandID=OperandId.add_own_srq_mod,
            arg1=e_optr_tgt['expressionID'], arg2=e_src_attr['expressionID'])
        e_rm_mod = self.ef.make(
            10, operandID=OperandId.rm_own_srq_mod,
            arg1=e_optr_tgt['expressionID'], arg2=e_src_attr['expressionID'])
        self.effect_row = {
            'preExpression': e_add_mod['expressionID'],
            'postExpression': e_rm_mod['expressionID']}

    def test_domain_self(self):
        self.make_etree('Self')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.get_log()), 1)

    def test_domain_char(self):
        self.make_etree('Char')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(
            modifier.tgt_filter, ModifierTargetFilter.owner_skillrq)
        self.assertEqual(modifier.tgt_domain, ModifierDomain.character)
        self.assertEqual(modifier.tgt_filter_extra_arg, 3412)
        self.assertEqual(modifier.tgt_attr, 1372)
        self.assertEqual(modifier.operator, ModifierOperator.post_percent)
        self.assertEqual(modifier.src_attr, 1156)
        self.assertEqual(len(self.get_log()), 0)

    def test_domain_ship(self):
        self.make_etree('Ship')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.get_log()), 1)

    def test_domain_target(self):
        self.make_etree('Target')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.get_log()), 1)

    def test_domain_other(self):
        self.make_etree('Other')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.get_log()), 1)
