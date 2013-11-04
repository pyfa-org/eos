#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from unittest.mock import Mock

from eos.fit.holder.mixin import SpecialAttribMixin
from eos.tests.fit.fit_testcase import FitTestCase


class TestHolderMixinSpecialAttrib(FitTestCase):

    def setUp(self):
        FitTestCase.setUp(self)
        self.mixin = SpecialAttribMixin()
        self.mixin.attributes = {}
        self.mixin.item = Mock()

    def test_tracking(self):
        self.mixin.item._tracking_speed_attribute_id = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.tracking_speed, 8)

    def test_optimal(self):
        self.mixin.item._range_attribute_id = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.optimal_range, 8)

    def test_falloff(self):
        self.mixin.item._falloff_attribute_id = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.falloff_range, 8)

    def test_cycle(self):
        self.mixin.item._duration_attribute_id = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.cycle_time, 8)

    def test_change(self):
        self.mixin.item._tracking_speed_attribute_id = 102
        self.mixin.attributes[102] = 8
        self.assertAlmostEqual(self.mixin.tracking_speed, 8)
        self.mixin.attributes[102] = 9
        self.assertAlmostEqual(self.mixin.tracking_speed, 9)

    def test_undescribed(self):
        self.mixin.attributes[102] = 8
        self.assertIsNone(self.mixin.tracking_speed)

    def test_no_attr(self):
        self.mixin.item._tracking_speed_attribute_id = 102
        self.assertIsNone(self.mixin.tracking_speed)
