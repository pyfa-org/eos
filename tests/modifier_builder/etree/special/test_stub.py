#===============================================================================
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
#===============================================================================


from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from eos.tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestStubInt0(ModBuilderTestCase):
    """Test parsing of trees describing integer-0 stub"""

    def test_build_success(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_int, expressionValue='0')
        e_post_stub = self.ef.make(2, operandID=Operand.def_int, expressionValue='0')
        effect_row = {
            'pre_expression_id': e_pre_stub['expressionID'],
            'post_expression_id': e_post_stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubInt1(ModBuilderTestCase):
    """Test parsing of trees describing integer-1 stub"""

    def test_build_success(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_int, expressionValue='1')
        e_post_stub = self.ef.make(2, operandID=Operand.def_int, expressionValue='1')
        effect_row = {
            'pre_expression_id': e_pre_stub['expressionID'],
            'post_expression_id': e_post_stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubBoolTrue(ModBuilderTestCase):
    """Test parsing of trees describing boolean-True stub"""

    def test_build_success(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_bool, expressionValue='True')
        e_post_stub = self.ef.make(2, operandID=Operand.def_bool, expressionValue='True')
        effect_row = {
            'pre_expression_id': e_pre_stub['expressionID'],
            'post_expression_id': e_post_stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubMixed(ModBuilderTestCase):
    """Test parsing of trees describing mixed form stubs"""

    def test_build_success(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_bool, expressionValue='True')
        e_post_stub = self.ef.make(2, operandID=Operand.def_int, expressionValue='0')
        effect_row = {
            'pre_expression_id': e_pre_stub['expressionID'],
            'post_expression_id': e_post_stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)
