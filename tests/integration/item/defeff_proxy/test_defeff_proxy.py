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


from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategoryId
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinDefEffProxy(ItemMixinTestCase):

    def make_item_with_defeff_attrib(self, defeff_attrib_name):
        attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        mod_effect1 = self.ch.effect(category=EffectCategoryId.passive, modifiers=[modifier])
        mod_effect2 = self.ch.effect(category=EffectCategoryId.online, modifiers=[modifier])
        def_effect = self.ch.effect(category=EffectCategoryId.active, **{defeff_attrib_name: attr.id})
        item = ModuleHigh(self.ch.type(
            attributes={attr.id: 50, src_attr.id: 2}, effects=(mod_effect1, mod_effect2, def_effect),
            default_effect=def_effect
        ).id)
        return item

    def test_cycle(self):
        fit = Fit()
        item = self.make_item_with_defeff_attrib('duration_attribute')
        fit.modules.high.append(item)
        # Verification
        # Cycle time is divided by 1000, as it's defined in ms
        self.assertAlmostEqual(item.cycle_time, 0.1)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_optimal(self):
        fit = Fit()
        item = self.make_item_with_defeff_attrib('range_attribute')
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.optimal_range, 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_falloff(self):
        fit = Fit()
        item = self.make_item_with_defeff_attrib('falloff_attribute')
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.falloff_range, 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_tracking(self):
        fit = Fit()
        item = self.make_item_with_defeff_attrib('tracking_speed_attribute')
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.tracking_speed, 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    # Various errors are tested here, but just for one of access points
    def test_optimal_no_source(self):
        fit = Fit(source=None)
        item = self.make_item_with_defeff_attrib('range_attribute')
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_optimal_no_defeff(self):
        attr = self.ch.attribute()
        effect = self.ch.effect(category=EffectCategoryId.active, range_attribute=attr.id)
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={attr.id: 50}, effects=[effect]).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_optimal_no_description(self):
        attr = self.ch.attribute()
        effect = self.ch.effect(category=EffectCategoryId.active)
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={attr.id: 50}, effects=[effect], default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_optimal_no_attr(self):
        attr = self.ch.attribute()
        effect = self.ch.effect(category=EffectCategoryId.active, range_attribute=attr.id)
        fit = Fit()
        item = ModuleHigh(self.ch.type(effects=[effect], default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.optimal_range)
        # Cleanup
        # Log entry appears on attempt to get undefined attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)
