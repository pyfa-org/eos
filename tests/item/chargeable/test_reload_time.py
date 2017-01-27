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


from unittest.mock import Mock

from eos.const.eve import Attribute, Effect
from eos.fit.item import ModuleHigh
from tests.item.item_testcase import ItemMixinTestCase


class TestItemMixinChargeReloadTime(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.item = ModuleHigh(type_id=None)
        self.item._eve_type = Mock()
        self.item._clear_volatile_attrs = Mock()
        self.item.attributes = {}

    def test_generic(self):
        self.item.attributes[Attribute.reload_time] = 5000.0
        self.item._eve_type.default_effect.id = 1008
        self.assertEqual(self.item.reload_time, 5.0)

    def test_generic_no_attribute(self):
        self.item._eve_type.default_effect.id = 1008
        self.assertIsNone(self.item.reload_time)

    def test_generic_no_eve_type(self):
        self.item.attributes[Attribute.reload_time] = 5000.0
        self.item._eve_type = None
        self.assertEqual(self.item.reload_time, 5.0)

    def test_generic_no_default_effect(self):
        self.item.attributes[Attribute.reload_time] = 5000.0
        self.item._eve_type.default_effect = None
        self.assertEqual(self.item.reload_time, 5.0)

    def test_combat_combat_laser(self):
        self.item.attributes[Attribute.reload_time] = 5000.0
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertEqual(self.item.reload_time, 1.0)

    def test_combat_mining_laser(self):
        self.item.attributes[Attribute.reload_time] = 5000.0
        self.item._eve_type.default_effect.id = Effect.mining_laser
        self.assertEqual(self.item.reload_time, 1.0)
