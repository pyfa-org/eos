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

from eos.fit.holder.item import Module, Charge
from eos.tests.fit.holderContainer.containerTestCase import ContainerTestCase


class TestDirectModuleCharge(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)

    def testFreeModuleNoneToNone(self):
        module = Module(1, charge=None)
        module.charge = None
        self.assertIsNone(module.charge)

    def testFreeModuleNoneToFreeCharge(self):
        module = Module(1, charge=None)
        charge = Charge(2)
        module.charge = charge
        self.assertIs(module.charge, charge)

    def testFreeModuleChargeToFreeCharge(self):
        module = Module(1, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        module.charge = charge1
        module.charge = charge2
        self.assertIs(module.charge, charge2)

    def testFreeModuleChargeToNone(self):
        module = Module(1, charge=None)
        charge = Charge(2)
        module.charge = charge
        module.charge = None
        self.assertIsNone(module.charge)

    def testFreeModuleNoneToBoundCharge(self):
        chargeFit = Mock()
        module = Module(1, charge=None)
        charge = Charge(2)
        charge._fit = chargeFit
        chargeFitCallsBefore = len(chargeFit.mock_calls)
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge)
        chargeFitCallsAfter = len(chargeFit.mock_calls)
        self.assertEqual(chargeFitCallsAfter - chargeFitCallsBefore, 0)
        self.assertIsNone(module.charge)

    def testFreeModuleChargeToBoundCharge(self):
        charge2Fit = Mock()
        module = Module(1, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        charge2._fit = charge2Fit
        module.charge = charge1
        charge2FitCallsBefore = len(charge2Fit.mock_calls)
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge2)
        charge2FitCallsAfter = len(charge2Fit.mock_calls)
        self.assertEqual(charge2FitCallsAfter - charge2FitCallsBefore, 0)
        self.assertIs(module.charge, charge1)