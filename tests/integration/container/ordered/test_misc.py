# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
from tests.integration.container.testcase import ContainerTestCase


class TestContainerOrderedMisc(ContainerTestCase):

    def test_len(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        self.assertEqual(len(fit.modules.high), 0)
        fit.modules.high.append(item1)
        self.assertEqual(len(fit.modules.high), 1)
        fit.modules.high.place(3, item2)
        self.assertEqual(len(fit.modules.high), 4)
        fit.modules.high.remove(item1)
        self.assertEqual(len(fit.modules.high), 3)
        fit.modules.high.remove(item2)
        self.assertEqual(len(fit.modules.high), 0)
        # Cleanup
        self.assert_item_buffers_empty(item1)
        self.assert_item_buffers_empty(item2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_contains(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        self.assertFalse(item1 in fit.modules.high)
        self.assertFalse(None in fit.modules.high)
        self.assertFalse(item2 in fit.modules.high)
        fit.modules.high.append(item1)
        self.assertTrue(item1 in fit.modules.high)
        self.assertFalse(None in fit.modules.high)
        self.assertFalse(item2 in fit.modules.high)
        fit.modules.high.place(3, item2)
        self.assertTrue(item1 in fit.modules.high)
        self.assertTrue(None in fit.modules.high)
        self.assertTrue(item2 in fit.modules.high)
        fit.modules.high.remove(item1)
        self.assertFalse(item1 in fit.modules.high)
        self.assertTrue(None in fit.modules.high)
        self.assertTrue(item2 in fit.modules.high)
        fit.modules.high.remove(item2)
        self.assertFalse(item1 in fit.modules.high)
        self.assertFalse(None in fit.modules.high)
        self.assertFalse(item2 in fit.modules.high)
        # Cleanup
        self.assert_item_buffers_empty(item1)
        self.assert_item_buffers_empty(item2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_iter(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        self.assertEqual(list(item for item in fit.modules.high), [])
        fit.modules.high.append(item1)
        self.assertEqual(list(item for item in fit.modules.high), [item1])
        fit.modules.high.place(3, item2)
        self.assertEqual(
            list(item for item in fit.modules.high), [item1, None, None, item2])
        fit.modules.high.remove(item1)
        self.assertEqual(
            list(item for item in fit.modules.high), [None, None, item2])
        fit.modules.high.remove(item2)
        self.assertEqual(list(item for item in fit.modules.high), [])
        # Cleanup
        self.assert_item_buffers_empty(item1)
        self.assert_item_buffers_empty(item2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_clear(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item1)
        fit.modules.high.place(3, item2)
        # Action
        fit.modules.high.clear()
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        # Cleanup
        self.assert_item_buffers_empty(item1)
        self.assert_item_buffers_empty(item2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_slice(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        fit.modules.high.append(item1)
        fit.modules.high.place(3, item2)
        slice_full = fit.modules.high[:]
        self.assertEqual(len(slice_full), 4)
        self.assertIs(slice_full[0], item1)
        self.assertIsNone(slice_full[1])
        self.assertIsNone(slice_full[2])
        self.assertIs(slice_full[3], item2)
        slice_positive = fit.modules.high[0:2]
        self.assertEqual(len(slice_positive), 2)
        self.assertIs(slice_positive[0], item1)
        self.assertIsNone(slice_positive[1])
        slice_negative = fit.modules.high[-2:]
        self.assertEqual(len(slice_negative), 2)
        self.assertIsNone(slice_negative[0])
        self.assertIs(slice_negative[1], item2)
        slice_step = fit.modules.high[::2]
        self.assertEqual(len(slice_step), 2)
        self.assertIs(slice_step[0], item1)
        self.assertIsNone(slice_step[1])
        # Cleanup
        self.assert_item_buffers_empty(item1)
        self.assert_item_buffers_empty(item2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_bool(self):
        fit = Fit()
        item = ModuleHigh(self.mktype().id)
        self.assertIs(bool(fit.modules.high), False)
        fit.modules.high.place(3, item)
        self.assertIs(bool(fit.modules.high), True)
        fit.modules.high.remove(item)
        self.assertIs(bool(fit.modules.high), False)
        # Cleanup
        self.assert_item_buffers_empty(item)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_view(self):
        fit = Fit()
        item1 = ModuleHigh(self.mktype().id)
        item2 = ModuleHigh(self.mktype().id)
        view = fit.modules.high.items()
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(item1 in view)
        self.assertFalse(item2 in view)
        self.assertFalse(None in view)
        fit.modules.high.append(item1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [item1])
        self.assertTrue(item1 in view)
        self.assertFalse(item2 in view)
        self.assertFalse(None in view)
        fit.modules.high.place(3, item2)
        self.assertEqual(len(view), 2)
        self.assertEqual(list(view), [item1, item2])
        self.assertTrue(item1 in view)
        self.assertTrue(item2 in view)
        self.assertFalse(None in view)
        fit.modules.high.free(item1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [item2])
        self.assertFalse(item1 in view)
        self.assertTrue(item2 in view)
        self.assertFalse(None in view)
        fit.modules.high.free(item2)
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(item1 in view)
        self.assertFalse(item2 in view)
        self.assertFalse(None in view)
        # Cleanup
        self.assert_item_buffers_empty(item1)
        self.assert_item_buffers_empty(item2)
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
