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


class TestContainerOrderedEquip(ContainerTestCase):

    def test_none_to_empty(self):
        fit = Fit()
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.equip(None)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_to_empty(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type().id)
        # Action
        fit.modules.high.equip(item)
        # Verification
        self.assertIs(len(fit.modules.high), 1)
        self.assertIs(fit.modules.high[0], item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_type_failure(self):
        fit = Fit()
        item = ModuleMed(self.ch.type().id)
        # Action
        with self.assertRaises(TypeError):
            fit.modules.high.equip(item)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        fit.modules.med.equip(item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_value_failure(self):
        fit = Fit()
        fit_other = Fit()
        item = ModuleHigh(self.ch.type().id)
        fit_other.modules.high.equip(item)
        # Action
        with self.assertRaises(ValueError):
            fit.modules.high.equip(item)
        # Verification
        self.assertIs(len(fit.modules.high), 0)
        self.assertIs(len(fit_other.modules.high), 1)
        self.assertIs(fit_other.modules.high[0], item)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_solid(self):
        fit = Fit()
        # Check case when all slots of list are filled
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        fit.modules.high.equip(item3)
        # Verification
        self.assertIs(len(fit.modules.high), 3)
        self.assertIs(fit.modules.high[2], item3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_item_first_hole(self):
        fit = Fit()
        # Check that leftmost empty slot is taken
        item1 = ModuleHigh(self.ch.type().id)
        item2 = ModuleHigh(self.ch.type().id)
        item3 = ModuleHigh(self.ch.type().id)
        item4 = ModuleHigh(self.ch.type().id)
        fit.modules.high.append(item1)
        fit.modules.high.insert(3, item2)
        fit.modules.high.insert(6, item3)
        # Action
        fit.modules.high.equip(item4)
        # Verification
        self.assertIs(len(fit.modules.high), 7)
        self.assertIs(fit.modules.high[1], item4)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
