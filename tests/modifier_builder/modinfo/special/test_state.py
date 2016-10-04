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


from eos.const.eos import EffectBuildStatus, State
from eos.const.eve import EffectCategory
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderModinfoState(ModBuilderTestCase):
    """Test parsing of YAML describing modifiers applied at different states"""

    def setUp(self):
        super().setUp()
        self.yaml = ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
            '  modifyingAttributeID: 11\n  operator: 6\n')

    def test_passive(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self.yaml
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(len(self.log), 0)

    def test_active(self):
        effect_row = {
            'effect_category': EffectCategory.active,
            'modifier_info': self.yaml
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(len(self.log), 0)

    def test_target(self):
        effect_row = {
            'effect_category': EffectCategory.target,
            'modifier_info': self.yaml
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(len(self.log), 0)

    def test_online(self):
        effect_row = {
            'effect_category': EffectCategory.online,
            'modifier_info': self.yaml
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(len(self.log), 0)

    def test_overload(self):
        effect_row = {
            'effect_category': EffectCategory.overload,
            'modifier_info': self.yaml
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(len(self.log), 0)

    def test_system(self):
        effect_row = {
            'effect_category': EffectCategory.system,
            'modifier_info': self.yaml
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(len(self.log), 0)
