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


from unittest.mock import Mock, call

from eos.fit import Fit
from eos.fit.exception import HolderAddError
from eos.tests.fit.holderContainer.containerTestCase import ContainerTestCase


class TestDirectHolderSystemWide(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.fit = Fit()
        self._setupDirectCheck(self.fit, 'systemWide')

    def testNoneToNone(self):
        fit = self.fit
        addCallsBefore = len(fit._addHolder.mock_calls)
        removeCallsBefore = len(fit._removeHolder.mock_calls)
        fit.systemWide = None
        addCallsAfter = len(fit._addHolder.mock_calls)
        removeCallsAfter = len(fit._removeHolder.mock_calls)
        self.assertEqual(addCallsAfter - addCallsBefore, 0)
        self.assertEqual(removeCallsAfter - removeCallsBefore, 0)
        self.assertIsNone(fit.systemWide)

    def testNoneToHolder(self):
        fit = self.fit
        holder = Mock(spec_set=())
        addCallsBefore = len(fit._addHolder.mock_calls)
        removeCallsBefore = len(fit._removeHolder.mock_calls)
        fit.systemWide = holder
        addCallsAfter = len(fit._addHolder.mock_calls)
        removeCallsAfter = len(fit._removeHolder.mock_calls)
        self.assertEqual(addCallsAfter - addCallsBefore, 1)
        self.assertEqual(fit._addHolder.mock_calls[-1], call(holder))
        self.assertEqual(removeCallsAfter - removeCallsBefore, 0)
        self.assertIs(fit.systemWide, holder)

    def testNoneToHolderFailure(self):
        fit = self.fit
        holder = Mock(spec_set=())
        fit._addHolder.side_effect = HolderAddError(holder)
        addCallsBefore = len(fit._addHolder.mock_calls)
        removeCallsBefore = len(fit._removeHolder.mock_calls)
        self.assertRaises(ValueError, fit.__setattr__, 'systemWide', holder)
        addCallsAfter = len(fit._addHolder.mock_calls)
        removeCallsAfter = len(fit._removeHolder.mock_calls)
        self.assertEqual(addCallsAfter - addCallsBefore, 1)
        self.assertEqual(fit._addHolder.mock_calls[-1], call(holder))
        self.assertEqual(removeCallsAfter - removeCallsBefore, 0)
        self.assertIsNone(fit.systemWide)

    def testHolderToHolder(self):
        fit = self.fit
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        fit.systemWide = holder1
        addCallsBefore = len(fit._addHolder.mock_calls)
        removeCallsBefore = len(fit._removeHolder.mock_calls)
        fit.systemWide = holder2
        addCallsAfter = len(fit._addHolder.mock_calls)
        removeCallsAfter = len(fit._removeHolder.mock_calls)
        self.assertEqual(addCallsAfter - addCallsBefore, 1)
        self.assertEqual(fit._addHolder.mock_calls[-1], call(holder2))
        self.assertEqual(removeCallsAfter - removeCallsBefore, 1)
        self.assertEqual(fit._removeHolder.mock_calls[-1], call(holder1))
        self.assertIs(fit.systemWide, holder2)

    def testHolderToHolderFailure(self):
        fit = self.fit
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        fit.systemWide = holder1
        normalSideEffect = fit._addHolder.side_effect
        customSideEffect = True

        def customizedSideEffect(holder):
            nonlocal customSideEffect
            if customSideEffect is True:
                customSideEffect = False
                nonlocal holder2
                raise HolderAddError(holder2)
            else:
                normalSideEffect(holder)

        fit._addHolder.side_effect = customizedSideEffect
        addCallsBefore = len(fit._addHolder.mock_calls)
        removeCallsBefore = len(fit._removeHolder.mock_calls)
        self.assertRaises(ValueError, fit.__setattr__, 'systemWide', holder2)
        addCallsAfter = len(fit._addHolder.mock_calls)
        removeCallsAfter = len(fit._removeHolder.mock_calls)
        self.assertEqual(addCallsAfter - addCallsBefore, 2)
        self.assertEqual(fit._addHolder.mock_calls[-2], call(holder2))
        self.assertEqual(fit._addHolder.mock_calls[-1], call(holder1))
        self.assertEqual(removeCallsAfter - removeCallsBefore, 1)
        self.assertEqual(fit._removeHolder.mock_calls[-1], call(holder1))
        self.assertIs(fit.systemWide, holder1)

    def testHolderToNone(self):
        fit = self.fit
        holder = Mock(spec_set=())
        fit.systemWide = holder
        addCallsBefore = len(fit._addHolder.mock_calls)
        removeCallsBefore = len(fit._removeHolder.mock_calls)
        fit.systemWide = None
        addCallsAfter = len(fit._addHolder.mock_calls)
        removeCallsAfter = len(fit._removeHolder.mock_calls)
        self.assertEqual(addCallsAfter - addCallsBefore, 0)
        self.assertEqual(removeCallsAfter - removeCallsBefore, 1)
        self.assertEqual(fit._removeHolder.mock_calls[-1], call(holder))
        self.assertIsNone(fit.systemWide)
