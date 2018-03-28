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


from eos import Fit
from eos import ModuleHigh
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemModuleChargeReloadTime(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.reload_time)

    def test_generic(self):
        fit = Fit()
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.reload_time: 5000.0},
            effects=[effect],
            default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.reload_time, 5.0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_attr_reload_absent(self):
        fit = Fit()
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            effects=[effect],
            default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.reload_time)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_defeff_absent(self):
        fit = Fit()
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.reload_time: 5000.0},
            effects=[effect]).id)
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.reload_time, 5.0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_not_loaded(self):
        fit = Fit()
        item = ModuleHigh(self.allocate_type_id())
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.reload_time)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
