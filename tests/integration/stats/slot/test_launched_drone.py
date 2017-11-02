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
from eos.const.eve import AttributeId, EffectCategoryId
from tests.integration.stats.stat_testcase import StatTestCase


class TestLaunchedDrone(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.max_active_drones)

    def test_output(self):
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr_id=AttributeId.max_active_drones,
            operator=ModifierOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        self.fit.character = Character(self.ch.type(
            attributes={AttributeId.max_active_drones: 3, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertEqual(self.fit.stats.launched_drones.total, 6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_char(self):
        # None for slot quantity when no ship
        self.fit.character = None
        # Verification
        self.assertIsNone(self.fit.stats.launched_drones.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_attr(self):
        # None for slot quantity when no attribute on ship
        self.fit.character = Character(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.launched_drones.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_empty(self):
        # Verification
        self.assertEqual(self.fit.stats.launched_drones.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_multiple(self):
        self.fit.drones.add(Drone(self.ch.type().id, state=State.online))
        self.fit.drones.add(Drone(self.ch.type().id, state=State.online))
        # Verification
        self.assertEqual(self.fit.stats.launched_drones.used, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_state(self):
        self.fit.subsystems.add(Subsystem(self.ch.type().id))
        # Verification
        self.assertEqual(self.fit.stats.launched_drones.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_other_item_class(self):
        self.fit.modules.med.append(
            ModuleMed(self.ch.type().id, state=State.online))
        # Verification
        self.assertEqual(self.fit.stats.launched_drones.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.character = Character(self.ch.type(
            attributes={AttributeId.max_active_drones: 3}).id)
        self.fit.drones.add(Drone(self.ch.type().id, state=State.online))
        self.fit.drones.add(Drone(self.ch.type().id, state=State.online))
        self.fit.source = None
        # Verification
        self.assertEqual(self.fit.stats.launched_drones.used, 0)
        self.assertIsNone(self.fit.stats.launched_drones.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
