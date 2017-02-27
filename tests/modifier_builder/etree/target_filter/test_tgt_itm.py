# ===============================================================================
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
# ===============================================================================


from eos.const.eos import EffectBuildStatus, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeTgtItm(ModBuilderTestCase):

    def make_etree(self, domain):
        e_tgt = self.ef.make(1, operandID=Operand.def_dom, expressionValue=domain)
        e_tgt_attr = self.ef.make(2, operandID=Operand.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(3, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(4, operandID=Operand.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            5, operandID=Operand.itm_attr,
            arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            6, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        e_add_mod = self.ef.make(
            7, operandID=Operand.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_rm_mod = self.ef.make(
            8, operandID=Operand.rm_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        self.effect_row = {
            'pre_expression': e_add_mod['expressionID'],
            'post_expression': e_rm_mod['expressionID']
        }

    def test_domain_self(self):
        self.make_etree('Self')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModifierTargetFilter.item)
        self.assertEqual(modifier.tgt_domain, ModifierDomain.self)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr, 9)
        self.assertEqual(modifier.operator, ModifierOperator.post_percent)
        self.assertEqual(modifier.src_attr, 327)
        self.assertEqual(len(self.log), 0)

    def test_domain_char(self):
        self.make_etree('Char')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModifierTargetFilter.item)
        self.assertEqual(modifier.tgt_domain, ModifierDomain.character)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr, 9)
        self.assertEqual(modifier.operator, ModifierOperator.post_percent)
        self.assertEqual(modifier.src_attr, 327)
        self.assertEqual(len(self.log), 0)

    def test_domain_ship(self):
        self.make_etree('Ship')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModifierTargetFilter.item)
        self.assertEqual(modifier.tgt_domain, ModifierDomain.ship)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr, 9)
        self.assertEqual(modifier.operator, ModifierOperator.post_percent)
        self.assertEqual(modifier.src_attr, 327)
        self.assertEqual(len(self.log), 0)

    def test_domain_target(self):
        self.make_etree('Target')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModifierTargetFilter.item)
        self.assertEqual(modifier.tgt_domain, ModifierDomain.target)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr, 9)
        self.assertEqual(modifier.operator, ModifierOperator.post_percent)
        self.assertEqual(modifier.src_attr, 327)
        self.assertEqual(len(self.log), 0)

    def test_domain_other(self):
        self.make_etree('Other')
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter, ModifierTargetFilter.item)
        self.assertEqual(modifier.tgt_domain, ModifierDomain.other)
        self.assertIsNone(modifier.tgt_filter_extra_arg)
        self.assertEqual(modifier.tgt_attr, 9)
        self.assertEqual(modifier.operator, ModifierOperator.post_percent)
        self.assertEqual(modifier.src_attr, 327)
        self.assertEqual(len(self.log), 0)
