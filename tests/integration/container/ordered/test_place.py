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


from eos import Fit
from eos import ModuleHigh
from eos import ModuleMed
from eos import SlotTakenError
from tests.integration.container.testcase import ContainerTestCase


class TestContainerOrderedPlace(ContainerTestCase):

    def test_item_outside(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item1)
        # Action
        fit.modules.high.place(3, item2)
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
        self.assertEqual(len(self.get_log()), 0)

    def test_none_outside(self):
        fit = Fit()
        item = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.place(3, None)
        # Verification
        self.assertIs(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item)
        # Cleanup
        fit.modules.high.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_onto_none(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        item3 = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item1)
        fit.modules.high.insert(3, item2)
        # Action
        fit.modules.high.place(1, item3)
        # Verification
        self.assertIs(len(fit.modules.high), 4)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIs(fit.modules.high[1], item3)
        self.assertIsNone(fit.modules.high[2])
        self.assertIs(fit.modules.high[3], item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.high.remove(item2)
        fit.modules.high.remove(item3)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_onto_none(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item1)
        fit.modules.high.insert(3, item2)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.place(1, None)
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
        self.assertEqual(len(self.get_log()), 0)

    def test_item_onto_item(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item1)
        # Action
        with self.assertRaises(SlotTakenError):
            fit.modules.high.place(0, item2)
        # Verification
        self.assertIs(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item1)
        # Cleanup
        fit.modules.high.remove(item1)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_onto_item(self):
        fit = Fit()
        item = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.place(0, None)
        # Verification
        self.assertIs(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item)
        # Cleanup
        fit.modules.high.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_outside_type_failure(self):
        fit = Fit()
        item = ModuleMed(self.mktype().id)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.place(2, item)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        fit.modules.med.place(0, item)
        # Cleanup
        fit.modules.med.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_outside_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item = ModuleHigh(self.mktype().id)
        fit_other.modules.high.append(item)
        # Action
        with self.assertRaises(ValueError):
            fit.modules.high.place(2, item)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        self.assertIs(len(fit_other.modules.high), 1)
        self.assertIs(fit_other.modules.high[0], item)
        # Cleanup
        fit_other.modules.high.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_onto_none_type_failure(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleMed(self.mktype().id)
        fit.modules.high.insert(1, item1)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.place(0, item2)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIsNone(fit.modules.high[0])
        self.assertIs(fit.modules.high[1], item1)
        fit.modules.med.place(0, item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit.modules.med.remove(item2)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_onto_none_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        fit.modules.high.insert(1, item1)
        fit_other.modules.high.append(item2)
        # Action
        with self.assertRaises(ValueError):
            fit.modules.high.place(0, item2)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIsNone(fit.modules.high[0])
        self.assertIs(fit.modules.high[1], item1)
        self.assertIs(len(fit_other.modules.high), 1)
        self.assertIs(fit_other.modules.high[0], item2)
        # Cleanup
        fit.modules.high.remove(item1)
        fit_other.modules.high.remove(item2)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)
