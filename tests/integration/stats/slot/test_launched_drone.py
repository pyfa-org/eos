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
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Attribute, EffectCategory
from tests.integration.stats.stat_testcase import StatTestCase


class TestLaunchedDrone(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.max_active_drones)

    def test_output(self):
        src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=Attribute.max_active_drones,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        mod_effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        fit = Fit()
        fit.character = Character(self.ch.type(
            effects=[mod_effect], attributes={Attribute.max_active_drones: 3, src_attr.id: 2}
        ).id)
        # Verification
        self.assertEqual(fit.stats.launched_drones.total, 6)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_char(self):
        # None for slot amount when no ship
        fit = Fit()
        fit.character = None
        # Verification
        self.assertIsNone(fit.stats.launched_drones.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        fit = Fit()
        fit.character = Character(self.ch.type().id)
        # Verification
        self.assertIsNone(fit.stats.launched_drones.total)
        # Cleanup
        # Log entry is due to inability to calculate requested attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_use_empty(self):
        fit = Fit()
        # Verification
        self.assertEqual(fit.stats.launched_drones.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_multiple(self):
        fit = Fit()
        fit.drones.add(Drone(self.ch.type().id, state=State.online))
        fit.drones.add(Drone(self.ch.type().id, state=State.online))
        # Verification
        self.assertEqual(fit.stats.launched_drones.used, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_state(self):
        fit = Fit()
        fit.subsystems.add(Subsystem(self.ch.type().id))
        # Verification
        self.assertEqual(fit.stats.launched_drones.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_other_item_class(self):
        fit = Fit()
        fit.modules.med.append(ModuleMed(self.ch.type().id, state=State.online))
        # Verification
        self.assertEqual(fit.stats.launched_drones.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit()
        fit.character = Character(self.ch.type(attributes={Attribute.max_active_drones: 3}).id)
        fit.drones.add(Drone(self.ch.type().id, state=State.online))
        fit.drones.add(Drone(self.ch.type().id, state=State.online))
        fit.source = None
        # Verification
        self.assertEqual(fit.stats.launched_drones.used, 0)
        self.assertIsNone(fit.stats.launched_drones.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
