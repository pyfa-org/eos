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
from tests.integration.container.container_testcase import ContainerTestCase


class TestContainerOrderedInsert(ContainerTestCase):

    def test_item_to_zero(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.insert(0, item3)
        # Verification
        self.assertIs(len(fit.modules.high), 3)
        self.assertIs(fit.modules.high[0], item3)
        self.assertIs(fit.modules.high[1], item1)
        self.assertIs(fit.modules.high[2], item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        fit.modules.high.remove(item3)
        self.assert_fit_buffers_empty(fit)

    def test_item_to_end(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.insert(2, item3)
        # Verification
        self.assertIs(len(fit.modules.high), 3)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIs(fit.modules.high[1], item2)
        self.assertIs(fit.modules.high[2], item3)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        fit.modules.high.remove(item3)
        self.assert_fit_buffers_empty(fit)

    def test_item_outside(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        # Action
        fit.modules.high.insert(3, item2)
        # Verification
        self.assertIs(len(fit.modules.high), 4)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIsNone(fit.modules.high[1])
        self.assertIsNone(fit.modules.high[2])
        self.assertIs(fit.modules.high[3], item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        self.assert_fit_buffers_empty(fit)

    def test_item_inside_type_failure(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleMed(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.insert(1, item3)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIs(fit.modules.high[1], item2)
        fit.modules.med.insert(0, item3)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        fit.modules.med.remove(item3)
        self.assert_fit_buffers_empty(fit)

    def test_item_inside_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        fit_other.modules.high.append(item3)
        # Action
        with self.assertRaises(ValueError):
            fit.modules.high.insert(1, item3)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIs(fit.modules.high[1], item2)
        self.assertIs(len(fit_other.modules.high), 1)
        self.assertIs(fit_other.modules.high[0], item3)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        fit_other.modules.high.remove(item3)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_item_outside_type_failure(self):
        fit = Fit()
        item = ModuleMed(self.ch.type().id)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.insert(4, item)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        fit.modules.med.insert(0, item)
        # Cleanup
        fit.modules.med.remove(item)
        self.assert_fit_buffers_empty(fit)

    def test_item_outside_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item = ModuleHigh(self.ch.type().id)
        fit_other.modules.high.append(item)
        # Action
        with self.assertRaises(ValueError):
            fit.modules.high.insert(4, item)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        self.assertIs(len(fit_other.modules.high), 1)
        self.assertIs(fit_other.modules.high[0], item)
        # Cleanup
        fit_other.modules.high.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_none_inside(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.insert(1, None)
        # Verification
        self.assertIs(len(fit.modules.high), 3)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIsNone(fit.modules.high[1])
        self.assertIs(fit.modules.high[2], item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        self.assert_fit_buffers_empty(fit)

    def test_none_outside(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.insert(6, None)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIs(fit.modules.high[1], item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        self.assert_fit_buffers_empty(fit)
