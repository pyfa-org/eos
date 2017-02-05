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


import logging

from eos.const.eos import EffectBuildStatus, State
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeState(ModBuilderTestCase):

    def make_etree(self, effect_category):
        e_tgt = self.ef.make(1, operandID=Operand.def_dom, expressionValue='Ship')
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
            'post_expression': e_rm_mod['expressionID'],
            'effect_category': effect_category
        }

    def test_passive(self):
        self.make_etree(EffectCategory.passive)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(len(self.log), 0)

    def test_active(self):
        self.make_etree(EffectCategory.active)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(len(self.log), 0)

    def test_target(self):
        self.make_etree(EffectCategory.target)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(len(self.log), 0)

    def test_area(self):
        self.make_etree(EffectCategory.area)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'effect 1, building 1 modifiers: 1 build errors'
        self.assertEqual(log_record.msg, expected)

    def test_online(self):
        self.make_etree(EffectCategory.online)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(len(self.log), 0)

    def test_overload(self):
        self.make_etree(EffectCategory.overload)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(len(self.log), 0)

    def test_dungeon(self):
        self.make_etree(EffectCategory.dungeon)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'effect 1, building 1 modifiers: 1 build errors'
        self.assertEqual(log_record.msg, expected)

    def test_system(self):
        self.make_etree(EffectCategory.system)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(len(self.log), 0)
