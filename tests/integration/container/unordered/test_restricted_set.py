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


class TestContainerRestrictedSet(ContainerTestCase):

    def test_add_none(self):
        fit = Fit()
        # Action
        self.assertRaises(TypeError, fit.skills.add, None)
        # Verification
        self.assertEqual(len(fit.skills), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_add_item(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item = Skill(item_eve_type.id)
        # Action
        fit.skills.add(item)
        # Verification
        self.assertEqual(len(fit.skills), 1)
        self.assertIs(fit.skills[item_eve_type.id], item)
        self.assertIn(item, fit.skills)
        self.assertIn(item_eve_type.id, fit.skills)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_add_item_type_failure(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item = Implant(item_eve_type.id)
        # Action
        self.assertRaises(TypeError, fit.skills.add, item)
        # Verification
        self.assertEqual(len(fit.skills), 0)
        self.assertNotIn(item, fit.skills)
        self.assertNotIn(item_eve_type.id, fit.skills)
        fit.implants.add(item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_add_item_value_failure_has_fit(self):
        fit = Fit()
        fit_other = Fit()
        item_eve_type = self.ch.type()
        item = Skill(item_eve_type.id)
        fit_other.skills.add(item)
        # Action
        self.assertRaises(ValueError, fit.skills.add, item)
        # Verification
        self.assertEqual(len(fit.skills), 0)
        self.assertEqual(len(fit_other.skills), 1)
        self.assertIs(fit_other.skills[item_eve_type.id], item)
        self.assertIn(item, fit_other.skills)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_add_item_value_failure_existing_type_id(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item1 = Skill(item_eve_type.id)
        item2 = Skill(item_eve_type.id)
        fit.skills.add(item1)
        # Action
        self.assertRaises(ValueError, fit.skills.add, item2)
        # Verification
        self.assertEqual(len(fit.skills), 1)
        self.assertIs(fit.skills[item_eve_type.id], item1)
        self.assertIn(item1, fit.skills)
        self.assertIn(item_eve_type.id, fit.skills)
        fit.skills.remove(item1)
        fit.skills.add(item2)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_remove_item(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item = Skill(item_eve_type.id)
        fit.skills.add(item)
        # Action
        fit.skills.remove(item)
        # Verification
        self.assertEqual(len(fit.skills), 0)
        self.assertNotIn(item, fit.skills)
        self.assertNotIn(item_eve_type.id, fit.skills)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_remove_item_failure(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item = Skill(item_eve_type.id)
        # Action
        self.assertRaises(KeyError, fit.skills.remove, item)
        # Verification
        self.assertEqual(len(fit.skills), 0)
        self.assertNotIn(item, fit.skills)
        self.assertNotIn(item_eve_type.id, fit.skills)
        fit.skills.add(item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_delitem_item(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item = Skill(item_eve_type.id)
        fit.skills.add(item)
        # Action
        del fit.skills[item_eve_type.id]
        # Verification
        self.assertEqual(len(fit.skills), 0)
        self.assertNotIn(item, fit.skills)
        self.assertNotIn(item_eve_type.id, fit.skills)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_delitem_item_failure(self):
        fit = Fit()
        item_eve_type = self.ch.type()
        item = Skill(item_eve_type.id)
        fit.skills.add(item)
        # Action
        self.assertRaises(KeyError, fit.skills.__delitem__, item_eve_type.id + 1)
        # Verification
        self.assertEqual(len(fit.skills), 1)
        self.assertIn(item, fit.skills)
        self.assertIn(item_eve_type.id, fit.skills)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_clear(self):
        fit = Fit()
        item1_eve_type = self.ch.type()
        item1 = Skill(item1_eve_type.id)
        item2_eve_type = self.ch.type()
        item2 = Skill(item2_eve_type.id)
        fit.skills.add(item1)
        fit.skills.add(item2)
        # Action
        fit.skills.clear()
        # Verification
        self.assertEqual(len(fit.skills), 0)
        self.assertNotIn(item1, fit.skills)
        self.assertNotIn(item1_eve_type.id, fit.skills)
        self.assertNotIn(item2, fit.skills)
        self.assertNotIn(item2_eve_type.id, fit.skills)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
