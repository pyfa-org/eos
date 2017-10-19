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


class TestContainerSet(ContainerTestCase):

    def test_add_none(self):
        fit = Fit()
        # Action
        with self.assertRaises(TypeError):
            fit.implants.add(None)
        # Verification
        self.assertEqual(len(fit.implants), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_add_item(self):
        fit = Fit()
        item = Implant(self.ch.type().id)
        # Action
        fit.implants.add(item)
        # Verification
        self.assertEqual(len(fit.implants), 1)
        self.assertIn(item, fit.implants)
        # Cleanup
        fit.implants.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_add_item_type_failure(self):
        fit = Fit()
        item = Booster(self.ch.type().id)
        # Action
        with self.assertRaises(TypeError):
            fit.implants.add(item)
        # Verification
        self.assertEqual(len(fit.implants), 0)
        fit.boosters.add(item)
        # Cleanup
        fit.boosters.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_add_item_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item = Implant(self.ch.type().id)
        fit_other.implants.add(item)
        # Action
        with self.assertRaises(ValueError):
            fit.implants.add(item)
        # Verification
        self.assertEqual(len(fit.implants), 0)
        self.assertEqual(len(fit_other.implants), 1)
        self.assertIn(item, fit_other.implants)
        # Cleanup
        fit_other.implants.remove(item)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assertEqual(len(self.get_log()), 0)

    def test_remove_item(self):
        fit = Fit()
        item = Implant(self.ch.type().id)
        fit.implants.add(item)
        # Action
        fit.implants.remove(item)
        # Verification
        self.assertEqual(len(fit.implants), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_remove_item_failure(self):
        fit = Fit()
        item = Implant(self.ch.type().id)
        # Action
        with self.assertRaises(KeyError):
            fit.implants.remove(item)
        # Verification
        self.assertEqual(len(fit.implants), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_clear(self):
        fit = Fit()
        item1 = Implant(self.ch.type().id)
        item2 = Implant(self.ch.type().id)
        fit.implants.add(item1)
        fit.implants.add(item2)
        # Action
        fit.implants.clear()
        # Verification
        self.assertEqual(len(fit.implants), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
