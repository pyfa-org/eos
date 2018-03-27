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
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemMixinDefEffProxy(ItemMixinTestCase):

    def make_item_with_defeff_attr(self, defeff_attr_name):
        attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        mod_effect2 = self.mkeffect(
            category_id=EffectCategoryId.online,
            modifiers=[modifier])
        def_effect = self.mkeffect(
            category_id=EffectCategoryId.active,
            **{defeff_attr_name: attr.id})
        item = ModuleHigh(self.mktype(
            attrs={attr.id: 50, src_attr.id: 2},
            effects=(mod_effect1, mod_effect2, def_effect),
            default_effect=def_effect).id)
        return item

    def test_cycle(self):
        fit = Fit()
        item = self.make_item_with_defeff_attr('duration_attr_id')
        fit.modules.high.append(item)
        # Verification
        # Cycle time is divided by 1000, as it's defined in ms
        self.assertAlmostEqual(item.cycle_time, 0.1)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_optimal(self):
        fit = Fit()
        item = self.make_item_with_defeff_attr('range_attr_id')
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.optimal_range, 100)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_falloff(self):
        fit = Fit()
        item = self.make_item_with_defeff_attr('falloff_attr_id')
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.falloff_range, 100)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_tracking(self):
        fit = Fit()
        item = self.make_item_with_defeff_attr('tracking_speed_attr_id')
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.tracking_speed, 100)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    # Various errors are tested here, but just for one of access points
    def test_optimal_source_none(self):
        fit = Fit(source=None)
        item = self.make_item_with_defeff_attr('range_attr_id')
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_optimal_no_defeff(self):
        attr = self.mkattr()
        effect = self.mkeffect(
            category_id=EffectCategoryId.active,
            range_attr_id=attr.id)
        fit = Fit()
        item = ModuleHigh(self.mktype(
            attrs={attr.id: 50}, effects=[effect]).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_optimal_no_description(self):
        attr = self.mkattr()
        effect = self.mkeffect(category_id=EffectCategoryId.active)
        fit = Fit()
        item = ModuleHigh(self.mktype(
            attrs={attr.id: 50},
            effects=[effect],
            default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_optimal_no_attr(self):
        attr = self.mkattr()
        effect = self.mkeffect(
            category_id=EffectCategoryId.active,
            range_attr_id=attr.id)
        fit = Fit()
        item = ModuleHigh(self.mktype(
            effects=[effect],
            default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
