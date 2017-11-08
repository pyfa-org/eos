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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.stats.stats_testcase import StatsTestCase


class TestRig(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.ch.attr(attribute_id=AttributeId.rig_slots)
        self.effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category_id=EffectCategoryId.passive)

    def test_output(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 3}).id)
        # Verification
        self.assertEqual(self.fit.stats.rig_slots.total, 3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_ship(self):
        # None for slot quantity when no ship
        # Verification
        self.assertIsNone(self.fit.stats.rig_slots.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_attr(self):
        # None for slot quantity when no attribute on ship
        self.fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.rig_slots.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_empty(self):
        # Verification
        self.assertEqual(self.fit.stats.rig_slots.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_multiple(self):
        self.fit.rigs.add(Rig(self.ch.type(effects=[self.effect]).id))
        self.fit.rigs.add(Rig(self.ch.type(effects=[self.effect]).id))
        # Verification
        self.assertEqual(self.fit.stats.rig_slots.used, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_disabled_effect(self):
        item1 = Rig(self.ch.type(effects=[self.effect]).id)
        item2 = Rig(self.ch.type(effects=[self.effect]).id)
        item2.set_effect_mode(self.effect.id, EffectMode.force_stop)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        # Verification
        self.assertEqual(self.fit.stats.rig_slots.used, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_other_item_class(self):
        self.fit.modules.med.append(
            ModuleMed(self.ch.type(effects=[self.effect]).id))
        # Verification
        self.assertEqual(self.fit.stats.rig_slots.used, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 3}).id)
        self.fit.rigs.add(Rig(self.ch.type(effects=[self.effect]).id))
        self.fit.rigs.add(Rig(self.ch.type(effects=[self.effect]).id))
        self.fit.source = None
        # Verification
        self.assertEqual(self.fit.stats.rig_slots.used, 0)
        self.assertIsNone(self.fit.stats.rig_slots.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
