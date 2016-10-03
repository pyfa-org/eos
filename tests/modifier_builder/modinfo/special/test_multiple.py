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
from eos.const.eve import EffectCategory
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderModinfoMultiple(ModBuilderTestCase):
    """Test how modifier builder behaves if there're multiple modifiers in YAML"""

    def test_multiple(self):
        effect_row = {
            'effect_category': EffectCategory.passive,
            'modifier_info': ('- domain: shipID\n  func: ItemModifier\n  modifiedAttributeID: 22\n'
                '  modifyingAttributeID: 11\n  operator: 6\n- domain: charID\n  func: ItemModifier\n'
                '  modifiedAttributeID: 33\n  modifyingAttributeID: 44\n  operator: 7\n')
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 2)
        self.assertEqual(len(self.log), 0)
