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


class TestContainerOrderedFree(ContainerTestCase):

    def test_none(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        self.assertRaises(ValueError, fit.modules.high.free, None)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIs(fit.modules.high[1], item2)
        # Cleanup
        fit.modules.high.free(item1)
        # Action
        fit.modules.high.free(None)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIsNone(fit.modules.high[0])
        self.assertIs(fit.modules.high[1], item2)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.free(item1)
        # Verification
        self.assertIs(len(fit.modules.high), 2)
        self.assertIsNone(fit.modules.high[0])
        self.assertIs(fit.modules.high[1], item2)
        # Action
        fit.modules.high.free(item2)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_failure(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        # Action
        self.assertRaises(ValueError, fit.modules.high.free, item2)
        # Verification
        self.assertEqual(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item1)
        # Cleanup
        fit.modules.high.free(item1)
        # Action
        self.assertRaises(ValueError, fit.modules.high.free, item1)
        # Verification
        self.assertEqual(len(fit.modules.high), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_after_nones(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.place(3, item2)
        fit.modules.high.place(6, item3)
        # Action
        fit.modules.high.free(item2)
        # Verification
        self.assertEqual(len(fit.modules.high), 7)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIsNone(fit.modules.high[1])
        self.assertIsNone(fit.modules.high[2])
        self.assertIsNone(fit.modules.high[3])
        self.assertIsNone(fit.modules.high[4])
        self.assertIsNone(fit.modules.high[5])
        self.assertIs(fit.modules.high[6], item3)
        # Action
        fit.modules.high.free(item3)
        # Verification
        self.assertEqual(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item1)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_index_item(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.free(0)
        # Verification
        self.assertEqual(len(fit.modules.high), 2)
        self.assertIsNone(fit.modules.high[0])
        self.assertIs(fit.modules.high[1], item2)
        # Action
        fit.modules.high.free(1)
        # Verification
        self.assertEqual(len(fit.modules.high), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_index_none(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type().id)
        fit.modules.high.place(1, item)
        # Action
        fit.modules.high.free(0)
        # Verification
        self.assertEqual(len(fit.modules.high), 2)
        self.assertIsNone(fit.modules.high[0])
        self.assertIs(fit.modules.high[1], item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_index_after_nones(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.place(3, item2)
        fit.modules.high.place(6, item3)
        # Action
        fit.modules.high.free(3)
        # Verification
        self.assertEqual(len(fit.modules.high), 7)
        self.assertIs(fit.modules.high[0], item1)
        self.assertIsNone(fit.modules.high[1])
        self.assertIsNone(fit.modules.high[2])
        self.assertIsNone(fit.modules.high[3])
        self.assertIsNone(fit.modules.high[4])
        self.assertIsNone(fit.modules.high[5])
        self.assertIs(fit.modules.high[6], item3)
        # Action
        fit.modules.high.free(6)
        # Verification
        self.assertEqual(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item1)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_index_outside(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item)
        # Action
        self.assertRaises(IndexError, fit.modules.high.free, 5)
        # Verification
        self.assertEqual(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
