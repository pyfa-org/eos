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

from eos.const.eve import Attribute
from eos.data.source import Source
from eos.fit.holder.container import HolderSet
from eos.fit.holder.item import Ship
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinTankingHp(FitTestCase):

    def setUp(self):
        super().setUp()
        self.holder = Ship(type_id=None)
        self.holder._clear_volatile_attrs = Mock()
        self.holder.attributes = {}

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderSet(fit, Ship)
        return fit

    def test_generic(self):
        self.holder.attributes[Attribute.hp] = 8
        self.holder.attributes[Attribute.armor_hp] = 10
        self.holder.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(self.holder.hp.hull, 8)
        self.assertAlmostEqual(self.holder.hp.armor, 10)
        self.assertAlmostEqual(self.holder.hp.shield, 12)
        self.assertAlmostEqual(self.holder.hp.total, 30)

    def test_unspecified(self):
        self.assertIsNone(self.holder.hp.hull)
        self.assertIsNone(self.holder.hp.armor)
        self.assertIsNone(self.holder.hp.shield)
        self.assertIsNone(self.holder.hp.total)
