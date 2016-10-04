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


from unittest.mock import Mock

from eos.const.eve import Attribute, Effect
from eos.fit.holder.item import ModuleHigh
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinChargeReloadTime(FitTestCase):

    def setUp(self):
        super().setUp()
        self.holder = ModuleHigh(type_id=None)
        self.holder.item = Mock()
        self.holder._clear_volatile_attrs = Mock()
        self.holder.attributes = {}

    def test_generic(self):
        self.holder.attributes[Attribute.reload_time] = 5000.0
        self.holder.item.default_effect.id = 1008
        self.assertEqual(self.holder.reload_time, 5.0)

    def test_generic_no_attribute(self):
        self.holder.item.default_effect.id = 1008
        self.assertIsNone(self.holder.reload_time)

    def test_generic_no_item(self):
        self.holder.attributes[Attribute.reload_time] = 5000.0
        self.holder.item = None
        self.assertEqual(self.holder.reload_time, 5.0)

    def test_generic_no_default_effect(self):
        self.holder.attributes[Attribute.reload_time] = 5000.0
        self.holder.item.default_effect = None
        self.assertEqual(self.holder.reload_time, 5.0)

    def test_combat_combat_laser(self):
        self.holder.attributes[Attribute.reload_time] = 5000.0
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertEqual(self.holder.reload_time, 1.0)

    def test_combat_mining_laser(self):
        self.holder.attributes[Attribute.reload_time] = 5000.0
        self.holder.item.default_effect.id = Effect.mining_laser
        self.assertEqual(self.holder.reload_time, 1.0)
