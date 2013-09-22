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

from eos.const.eos import State
from eos.fit.holder.container import HolderList
from eos.fit.holder.item import Module, Charge
from eos.tests.fit.fitTestCase import FitTestCase


class TestModuleCharge(FitTestCase):
    """
    Everything related to charge switching and
    addition, executed on the level of holders
    and fit, is tested here.
    """

    def setUp(self):
        FitTestCase.setUp(self)
        # This variable will control check of
        # module <-> charge link
        self.expectModuleChargeLink = None

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.ordered = HolderList(fit)
        return fit

    def customMembershipCheck(self, fit, holder):
        # If link variable is True, we make sure
        # there's link between module and charge upon
        # addition to both of trackers. If False, we
        # ensure there's no link.
        if self.expectModuleChargeLink is True:
            if hasattr(holder, 'charge'):
                self.assertIn(holder, fit.ordered)
                charge = holder.charge
                self.assertIsNotNone(charge)
                self.assertIs(charge.container, holder)
                other = holder._other
                self.assertIs(other, charge)
                self.assertIs(other._other, holder)
            if hasattr(holder, 'container'):
                self.assertNotIn(holder, fit.ordered)
                container = holder.container
                self.assertIsNotNone(container)
                self.assertIs(container.charge, holder)
                other = holder._other
                self.assertIs(other, container)
                self.assertIs(other._other, holder)
        elif self.expectModuleChargeLink is False:
            self.assertIn(holder, fit.ordered)
            if hasattr(holder, 'charge'):
                self.assertIsNone(holder.charge)
            if hasattr(holder, 'container'):
                self.assertIsNone(holder.container)
            self.assertIsNone(holder._other)


    def testDetachedModuleNoneToNone(self):
        module = Module(1, state=State.active, charge=None)
        # Action
        module.charge = None
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)

    def testDetachedModuleNoneToFreeCharge(self):
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        # Action
        module.charge = charge
        # Checks
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)

    def testDetachedModuleChargeToFreeCharge(self):
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Checks
        self.assertIs(module.charge, charge2)
        self.assertIs(module._other, charge2)
        self.assertIsNone(charge1.container)
        self.assertIsNone(charge1._other)
        self.assertIs(charge2.container, module)
        self.assertIs(charge2._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge1._fit)
        self.assertIsNone(charge2._fit)

    def testDetachedModuleChargeToNone(self):
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        # Action
        module.charge = None
        # Checks
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)

    def testDetachedModuleNoneToBoundCharge(self):
        fitOther = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fitOther.ordered.append(charge)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge)
        # Checks
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIsNone(module._fit)
        self.assertIs(charge._fit, fitOther)
        # Misc
        fitOther.ordered.remove(charge)
        self.assertFitBuffersEmpty(fitOther)

    def testDetachedModuleChargeToBoundCharge(self):
        fitOther = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fitOther.ordered.append(charge2)
        module.charge = charge1
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge2)
        # Checks
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIs(module._other, charge1)
        self.assertIs(module.charge, charge1)
        self.assertIs(charge1._other, module)
        self.assertIs(charge1.container, module)
        self.assertIsNone(charge2._other)
        self.assertIsNone(charge2.container)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fitOther)
        # Misc
        fitOther.ordered.remove(charge2)
        self.assertFitBuffersEmpty(fitOther)

    def testDetachedFitNoneToNone(self):
        fit = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        fit.ordered.append(module)
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testDetachedFitNoneToFreeCharge(self):
        fit = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        # Action
        module.charge = charge
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testDetachedFitChargeToFreeCharge(self):
        fit = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        module.charge = charge1
        # Action
        module.charge = charge2
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(module.charge, charge2)
        self.assertIs(module._other, charge2)
        self.assertIsNone(charge1.container)
        self.assertIsNone(charge1._other)
        self.assertIs(charge2.container, module)
        self.assertIs(charge2._other, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testDetachedFitChargeToNone(self):
        fit = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        module.charge = charge
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        # Misc
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testDetachedFitNoneToBoundCharge(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        fitOther.ordered.append(charge)
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fitOther)
        # Misc
        fit.ordered.remove(module)
        fitOther.ordered.remove(charge)
        self.assertFitBuffersEmpty(fit)
        self.assertFitBuffersEmpty(fitOther)

    def testDetachedFitChargeToBoundCharge(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        fitOther.ordered.append(charge2)
        module.charge = charge1
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIs(module.charge, charge1)
        self.assertIs(module._other, charge1)
        self.assertIs(charge1.container, module)
        self.assertIs(charge1._other, module)
        self.assertIsNone(charge2.container)
        self.assertIsNone(charge2._other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge1._fit, fit)
        self.assertIs(charge2._fit, fitOther)
        # Misc
        fit.ordered.remove(module)
        fitOther.ordered.remove(charge2)
        self.assertFitBuffersEmpty(fit)
        self.assertFitBuffersEmpty(fitOther)

    def testDetachedFitAddChargedModule(self):
        fit = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        # Action
        fit.ordered.append(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], module)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testDetachedFitAddRemovedModule(self):
        fit = self.makeFit()
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        fit.ordered.append(module)
        # Action
        fit.ordered.remove(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testAttachedFitNoneToNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        fit.ordered.append(module)
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIs(module._fit, fit)
        # Misc
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testAttachedFitNoneToFreeCharge(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        self.expectModuleChargeLink = True
        # Action
        module.charge = charge
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.lt)
        self.assertEqual(fit.lt[charge], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.rt)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        self.expectModuleChargeLink = None
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testAttachedFitChargeToFreeCharge(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        module.charge = charge1
        self.expectModuleChargeLink = True
        # Action
        module.charge = charge2
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge2, fit.lt)
        self.assertEqual(fit.lt[charge2], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge2, fit.rt)
        self.assertEqual(fit.rt[charge2], {State.offline})
        self.assertIs(module.charge, charge2)
        self.assertIs(module._other, charge2)
        self.assertIsNone(charge1.container)
        self.assertIsNone(charge1._other)
        self.assertIs(charge2.container, module)
        self.assertIs(charge2._other, module)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge1._fit)
        self.assertIs(charge2._fit, fit)
        # Misc
        self.expectModuleChargeLink = None
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testAttachedFitChargeToNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        module.charge = charge
        self.expectModuleChargeLink = True
        # Action
        module.charge = None
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIs(module._fit, fit)
        self.assertIsNone(charge._fit)
        # Misc
        self.expectModuleChargeLink = None
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testAttachedFitNoneToBoundCharge(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        fit.ordered.append(module)
        fitOther.ordered.append(charge)
        self.expectModuleChargeLink = True
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(charge, fitOther.lt)
        self.assertEqual(fitOther.lt[charge], {State.offline})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(charge, fitOther.rt)
        self.assertEqual(fitOther.rt[charge], {State.offline})
        self.assertIsNone(module.charge)
        self.assertIsNone(module._other)
        self.assertIsNone(charge.container)
        self.assertIsNone(charge._other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fitOther)
        # Misc
        self.expectModuleChargeLink = None
        fit.ordered.remove(module)
        fitOther.ordered.remove(charge)
        self.assertFitBuffersEmpty(fit)
        self.assertFitBuffersEmpty(fitOther)

    def testAttachedFitChargeToBoundCharge(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge1 = Charge(2)
        charge2 = Charge(3)
        fit.ordered.append(module)
        fitOther.ordered.append(charge2)
        module.charge = charge1
        self.expectModuleChargeLink = True
        # Action
        self.assertRaises(ValueError, module.__setattr__, 'charge', charge2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge1, fit.lt)
        self.assertEqual(fit.lt[charge1], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge1, fit.rt)
        self.assertEqual(fit.rt[charge1], {State.offline})
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(charge2, fitOther.lt)
        self.assertEqual(fitOther.lt[charge2], {State.offline})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(charge2, fitOther.rt)
        self.assertEqual(fitOther.rt[charge2], {State.offline})
        self.assertIs(module.charge, charge1)
        self.assertIs(module._other, charge1)
        self.assertIs(charge1.container, module)
        self.assertIs(charge1._other, module)
        self.assertIsNone(charge2.container)
        self.assertIsNone(charge2._other)
        self.assertIs(module._fit, fit)
        self.assertIs(charge1._fit, fit)
        self.assertIs(charge2._fit, fitOther)
        # Misc
        self.expectModuleChargeLink = None
        fit.ordered.remove(module)
        fitOther.ordered.remove(charge2)
        self.assertFitBuffersEmpty(fit)
        self.assertFitBuffersEmpty(fitOther)

    def testAttachedFitAddChargedModule(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        self.expectModuleChargeLink = True
        # Action
        fit.ordered.append(module)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(module, fit.lt)
        self.assertEqual(fit.lt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.lt)
        self.assertEqual(fit.lt[charge], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(module, fit.rt)
        self.assertEqual(fit.rt[module], {State.offline, State.online, State.active})
        self.assertIn(charge, fit.rt)
        self.assertEqual(fit.rt[charge], {State.offline})
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], module)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIs(module._fit, fit)
        self.assertIs(charge._fit, fit)
        # Misc
        self.expectModuleChargeLink = None
        fit.ordered.remove(module)
        self.assertFitBuffersEmpty(fit)

    def testAttachedFitAddRemovedModule(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        module = Module(1, state=State.active, charge=None)
        charge = Charge(2)
        module.charge = charge
        fit.ordered.append(module)
        self.expectModuleChargeLink = True
        # Action
        fit.ordered.remove(module)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIs(module.charge, charge)
        self.assertIs(module._other, charge)
        self.assertIs(charge.container, module)
        self.assertIs(charge._other, module)
        self.assertIsNone(module._fit)
        self.assertIsNone(charge._fit)
        # Misc
        self.assertFitBuffersEmpty(fit)
