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


from eos.const.eos import EffectBuildStatus, Operator
from eos.const.eve import EffectCategory
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderModinfoOperator(ModBuilderTestCase):
    """Test parsing of YAML describing modifiers with different operators"""

    def _make_yaml(self, operator):
        yaml = ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
            '  modifyingAttributeID: 11\n  operator: {}\n')
        return yaml.format(operator)

    def test_preassign(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(-1)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.pre_assign)
        self.assertEqual(len(self.log), 0)

    def test_premul(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(0)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.pre_mul)
        self.assertEqual(len(self.log), 0)

    def test_prediv(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(1)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.pre_div)
        self.assertEqual(len(self.log), 0)

    def test_modadd(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(2)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.mod_add)
        self.assertEqual(len(self.log), 0)

    def test_modsub(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(3)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.mod_sub)
        self.assertEqual(len(self.log), 0)

    def test_postmul(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(4)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.post_mul)
        self.assertEqual(len(self.log), 0)

    def test_postdiv(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(5)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.post_div)
        self.assertEqual(len(self.log), 0)

    def test_postperc(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(6)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(len(self.log), 0)

    def test_postassign(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml(7)
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.operator, Operator.post_assign)
        self.assertEqual(len(self.log), 0)
