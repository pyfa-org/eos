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


from eos import *
from eos.const.eve import Attribute, Effect, EffectCategory
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinChargeReloadTime(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.reload_time)

    def test_generic(self):
        fit = Fit()
        effect = self.ch.effect(category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.reload_time: 5000.0}, effects=[effect], default_effect=effect
        ).id)
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.reload_time, 5.0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_generic_no_attribute(self):
        fit = Fit()
        effect = self.ch.effect(category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(effects=[effect], default_effect=effect).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.reload_time)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_generic_no_default_effect(self):
        fit = Fit()
        effect = self.ch.effect(category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(attributes={Attribute.reload_time: 5000.0}, effects=[effect]).id)
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.reload_time, 5.0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_combat_combat_laser(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.reload_time: 5000.0}, effects=[effect], default_effect=effect
        ).id)
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.reload_time, 1.0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_combat_mining_laser(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.mining_laser, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.reload_time: 5000.0}, effects=[effect], default_effect=effect
        ).id)
        fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.reload_time, 1.0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit()
        effect = self.ch.effect(category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.reload_time: 5000.0}, effects=[effect], default_effect=effect
        ).id)
        fit.modules.high.append(item)
        fit.source = None
        # Verification
        self.assertIsNone(item.reload_time)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)
