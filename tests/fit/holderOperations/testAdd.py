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


from unittest.mock import Mock, call, patch

from eos.const.eos import State
from eos.fit import Fit
from eos.fit.exception import HolderAddError
from eos.tests.fit.fitTestCase import FitTestCase


@patch('eos.fit.fit.RestrictionTracker')
@patch('eos.fit.fit.LinkTracker')
class TestFitAddHolder(FitTestCase):

    def testEosLess(self, *args):
        fit = Fit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        ltCallsBefore = len(fit._linkTracker.mock_calls)
        rtCallsBefore = len(fit._restrictionTracker.mock_calls)
        fit._addHolder(holder)
        ltCallsAfter = len(fit._linkTracker.mock_calls)
        rtCallsAfter = len(fit._restrictionTracker.mock_calls)
        self.assertEqual(ltCallsAfter - ltCallsBefore, 0)
        self.assertEqual(rtCallsAfter - rtCallsBefore, 0)
        self.assertIs(holder._fit, fit)
        fit._removeHolder(holder)
        self.assertFitBuffersEmpty(fit)

    def testEosLessCharge(self, *args):
        fit = Fit()
        holder = Mock(_fit=None, charge=None, state=State.active, spec_set=('_fit', 'charge', 'state'))
        charge = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        holder.charge = charge
        ltCallsBefore = len(fit._linkTracker.mock_calls)
        rtCallsBefore = len(fit._restrictionTracker.mock_calls)
        fit._addHolder(holder)
        ltCallsAfter = len(fit._linkTracker.mock_calls)
        rtCallsAfter = len(fit._restrictionTracker.mock_calls)
        self.assertEqual(ltCallsAfter - ltCallsBefore, 0)
        self.assertEqual(rtCallsAfter - rtCallsBefore, 0)
        self.assertIs(holder._fit, fit)
        self.assertIs(charge._fit, fit)
        fit._removeHolder(holder)
        self.assertFitBuffersEmpty(fit)

    def testEosLessAlreadyAssigned(self, *args):
        fit1 = Fit()
        fit2 = Fit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit1._addHolder(holder)
        ltCallsBefore = len(fit2._linkTracker.mock_calls)
        rtCallsBefore = len(fit2._restrictionTracker.mock_calls)
        self.assertRaises(HolderAddError, fit2._addHolder, holder)
        ltCallsAfter = len(fit2._linkTracker.mock_calls)
        rtCallsAfter = len(fit2._restrictionTracker.mock_calls)
        self.assertEqual(ltCallsAfter - ltCallsBefore, 0)
        self.assertEqual(rtCallsAfter - rtCallsBefore, 0)
        self.assertIs(holder._fit, fit1)
        fit1._removeHolder(holder)
        self.assertFitBuffersEmpty(fit1)
        self.assertFitBuffersEmpty(fit2)

    def testWithEos(self, *args):
        eos = Mock(spec_set=())
        fit = Fit(eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        ltCallsBefore = len(fit._linkTracker.mock_calls)
        rtCallsBefore = len(fit._restrictionTracker.mock_calls)
        fit._addHolder(holder)
        ltCallsAfter = len(fit._linkTracker.mock_calls)
        rtCallsAfter = len(fit._restrictionTracker.mock_calls)
        self.assertEqual(ltCallsAfter - ltCallsBefore, 2)
        self.assertEqual(fit._linkTracker.mock_calls[-2], call.addHolder(holder))
        self.assertEqual(fit._linkTracker.mock_calls[-1], call.enableStates(holder, {State.offline, State.online, State.active}))
        self.assertEqual(rtCallsAfter - rtCallsBefore, 1)
        self.assertEqual(fit._restrictionTracker.mock_calls[-1], call.enableStates(holder, {State.offline, State.online, State.active}))
        self.assertIs(holder._fit, fit)
        fit._removeHolder(holder)
        self.assertFitBuffersEmpty(fit)

    def testWithEosCharge(self, *args):
        eos = Mock(spec_set=())
        fit = Fit(eos)
        holder = Mock(_fit=None, charge=None, state=State.active, spec_set=('_fit', 'charge', 'state'))
        charge = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        holder.charge = charge
        ltCallsBefore = len(fit._linkTracker.mock_calls)
        rtCallsBefore = len(fit._restrictionTracker.mock_calls)
        fit._addHolder(holder)
        ltCallsAfter = len(fit._linkTracker.mock_calls)
        rtCallsAfter = len(fit._restrictionTracker.mock_calls)
        self.assertEqual(ltCallsAfter - ltCallsBefore, 4)
        self.assertEqual(fit._linkTracker.mock_calls[-4], call.addHolder(holder))
        self.assertEqual(fit._linkTracker.mock_calls[-3], call.enableStates(holder, {State.offline, State.online, State.active}))
        self.assertEqual(fit._linkTracker.mock_calls[-2], call.addHolder(charge))
        self.assertEqual(fit._linkTracker.mock_calls[-1], call.enableStates(charge, {State.offline}))
        self.assertEqual(rtCallsAfter - rtCallsBefore, 2)
        self.assertEqual(fit._restrictionTracker.mock_calls[-2], call.enableStates(holder, {State.offline, State.online, State.active}))
        self.assertEqual(fit._restrictionTracker.mock_calls[-1], call.enableStates(charge, {State.offline}))
        self.assertIs(holder._fit, fit)
        self.assertIs(charge._fit, fit)
        fit._removeHolder(holder)
        self.assertFitBuffersEmpty(fit)

    def testWithEosAlreadyAssigned(self, *args):
        eos = Mock(spec_set=())
        fit1 = Fit(eos)
        fit2 = Fit(eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit1._addHolder(holder)
        ltCallsBefore = len(fit2._linkTracker.mock_calls)
        rtCallsBefore = len(fit2._restrictionTracker.mock_calls)
        self.assertRaises(HolderAddError, fit2._addHolder, holder)
        ltCallsAfter = len(fit2._linkTracker.mock_calls)
        rtCallsAfter = len(fit2._restrictionTracker.mock_calls)
        self.assertEqual(ltCallsAfter - ltCallsBefore, 0)
        self.assertEqual(rtCallsAfter - rtCallsBefore, 0)
        self.assertIs(holder._fit, fit1)
        fit1._removeHolder(holder)
        self.assertFitBuffersEmpty(fit1)
        self.assertFitBuffersEmpty(fit2)