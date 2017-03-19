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
from tests.integration.stats.stat_testcase import StatTestCase


class TestRig(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.rig_slots)
        self.slot_effect = self.ch.effect(effect_id=Effect.rig_slot, category=EffectCategory.passive)

    def test_output(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.rig_slots: 3}).id)
        # Verification
        self.assertAlmostEqual(fit.stats.rig_slots.total, 3)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_ship(self):
        # None for slot amount when no ship
        fit = Fit()
        # Verification
        self.assertIsNone(fit.stats.rig_slots.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        fit = Fit()
        fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(fit.stats.rig_slots.total)
        # Cleanup
        # Log entry is due to inability to calculate requested attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_use_empty(self):
        fit = Fit()
        # Verification
        self.assertEqual(fit.stats.rig_slots.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_multiple(self):
        fit = Fit()
        fit.rigs.add(Rig(self.ch.type(effects=[self.slot_effect]).id))
        fit.rigs.add(Rig(self.ch.type(effects=[self.slot_effect]).id))
        # Verification
        self.assertEqual(fit.stats.rig_slots.used, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_other_item_class(self):
        fit = Fit()
        fit.modules.med.append(ModuleMed(self.ch.type(effects=[self.slot_effect]).id))
        # Verification
        self.assertEqual(fit.stats.rig_slots.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
