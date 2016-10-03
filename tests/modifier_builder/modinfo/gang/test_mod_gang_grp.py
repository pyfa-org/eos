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
from eos.const.eve import EffectCategory
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderModinfoModGangGrp(ModBuilderTestCase):
    """Test parsing of YAML describing gang-mates' items modification filtered by group"""

    def _make_yaml(self, domain):
        yaml = ('- domain: {}\n  func: GangGroupModifier\n  groupID: 55\n'
            '  modifiedAttributeID: 22\n  modifyingAttributeID: 11\n  operator: 6\n')
        return yaml.format(domain)

    def test_domain_ship(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml('shipID')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.gang)
        self.assertEqual(modifier.domain, Domain.ship)
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.src_attr, 11)
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(modifier.tgt_attr, 22)
        self.assertEqual(modifier.filter_type, FilterType.group)
        self.assertEqual(modifier.filter_value, 55)
        self.assertEqual(len(self.log), 0)

    def test_domain_char(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml('charID')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.gang)
        self.assertEqual(modifier.domain, Domain.character)
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.src_attr, 11)
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(modifier.tgt_attr, 22)
        self.assertEqual(modifier.filter_type, FilterType.group)
        self.assertEqual(modifier.filter_value, 55)
        self.assertEqual(len(self.log), 0)

    def test_domain_other(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml('otherID')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_domain_target(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml('targetID')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_domain_none(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': self._make_yaml('null')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
