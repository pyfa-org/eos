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

from eos.fit.holder.mixin.misc import DefaultEffectAttribMixin
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinSpecialAttrib(FitTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = DefaultEffectAttribMixin()
        self.mixin.attributes = {}
        self.mixin.item = Mock()

    def test_tracking(self):
        self.mixin.item.default_effect.tracking_speed_attribute = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.tracking_speed, 8)

    def test_optimal(self):
        self.mixin.item.default_effect.range_attribute = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.optimal_range, 8)

    def test_falloff(self):
        self.mixin.item.default_effect.falloff_attribute = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.falloff_range, 8)

    def test_cycle(self):
        self.mixin.item.default_effect.duration_attribute = 102
        self.mixin.attributes[102] = 800
        self.assertAlmostEqual(self.mixin.cycle_time, 0.8)

    def test_change(self):
        self.mixin.item.default_effect.tracking_speed_attribute = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.tracking_speed, 8)
        self.mixin.attributes[102] = 9
        self.assertAlmostEqual(self.mixin.tracking_speed, 9)

    def test_nodefault_effect(self):
        self.mixin.item.default_effect = None
        self.mixin.attributes[102] = 800
        self.assertIsNone(self.mixin.cycle_time)

    def test_no_description(self):
        self.mixin.item.default_effect.duration_attribute = None
        self.mixin.attributes[102] = 800
        self.assertIsNone(self.mixin.cycle_time)

    def test_no_attr(self):
        self.mixin.item.default_effect.duration_attribute = 102
        self.assertIsNone(self.mixin.cycle_time)
