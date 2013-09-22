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


from unittest.mock import patch

from eos.fit import Fit
from eos.tests.eosTestCase import EosTestCase


class FitTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assertObjectBuffersEmpty -- checks if fit has
    any holders assigned to it.
    self.makeFit -- create fit with all services replaced
    by mocks. Everything added to link tracker is stored in
    fit.lt in {holder: {enabled states}} format, everything
    added to restriction tracker is stored in fit.rt in
    {holder: {enabled states}} format. If any specific
    membership checks need to be performed upon holder
    addition to and removal from trackers, they can be
    specified in customMembershipCheck(fit, holder) of
    child classes.
    """

    def assertFitBuffersEmpty(self, fit):
        holderNum = 0
        # Check if we have anything in our single holder  storages
        singleHolders = ('character', 'ship', 'systemWide')
        for attrName in singleHolders:
            holder = getattr(fit, attrName, None)
            if holder is not None:
                holderNum += 1
        # Seek for multiple holder storages
        for attrName in dir(fit):
            if attrName.startswith("__") and attrName.endswith("__"):
                continue
            attrVal = getattr(fit, attrName)
            try:
                attrLen = len(attrVal)
            except TypeError:
                pass
            else:
                holderNum += attrLen
        if holderNum > 0:
            plu = 'y' if holderNum == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(holderNum, plu)
            self.fail(msg=msg)

    @patch('eos.fit.fit.RestrictionTracker')
    @patch('eos.fit.fit.LinkTracker')
    def makeFit(self, *args, eos=None):
        fit = Fit(eos=eos)
        fit.character = None
        self.__setupTrackerMemory(fit)
        return fit

    def __setupTrackerMemory(self, fit):
        # Buffer which will keep track of holders added to
        # link tracker
        # Format: {holder: {states}}
        fit.lt = {}

        def handleLtAddHolder(holder):
            self.assertNotIn(holder, fit.lt)
            fit.lt[holder] = set()
            if hasattr(self, 'customMembershipCheck'):
                self.customMembershipCheck(fit, holder)

        def handleLtEnableStates(holder, states):
            self.assertIn(holder, fit.lt)
            self.assertEqual(len(set(states).intersection(fit.lt[holder])), 0)
            fit.lt[holder].update(set(states))
            if hasattr(self, 'customMembershipCheck'):
                self.customMembershipCheck(fit, holder)

        def handleLtDisableStates(holder, states):
            self.assertIn(holder, fit.lt)
            self.assertEqual(len(set(states).difference(fit.lt[holder])), 0)
            fit.lt[holder].difference_update(set(states))
            if hasattr(self, 'customMembershipCheck'):
                self.customMembershipCheck(fit, holder)

        def handleLtRemoveHolder(holder):
            self.assertIn(holder, fit.lt)
            self.assertEqual(len(fit.lt[holder]), 0)
            del fit.lt[holder]
            if hasattr(self, 'customMembershipCheck'):
                self.customMembershipCheck(fit, holder)

        fit._linkTracker.addHolder.side_effect = handleLtAddHolder
        fit._linkTracker.enableStates.side_effect = handleLtEnableStates
        fit._linkTracker.disableStates.side_effect = handleLtDisableStates
        fit._linkTracker.removeHolder.side_effect = handleLtRemoveHolder

        # Buffer which will keep track of holders added to
        # restriction tracker
        # Format: {holder: {states}}
        fit.rt = {}

        def handleRtEnableStates(holder, states):
            if holder not in fit.rt:
                fit.rt[holder] = set()
            self.assertEqual(len(set(states).intersection(fit.rt[holder])), 0)
            fit.rt[holder].update(set(states))
            if hasattr(self, 'customMembershipCheck'):
                self.customMembershipCheck(fit, holder)

        def handleRtDisableStates(holder, states):
            self.assertIn(holder, fit.rt)
            self.assertEqual(len(set(states).difference(fit.rt[holder])), 0)
            fit.rt[holder].difference_update(set(states))
            if len(fit.rt[holder]) == 0:
                del fit.rt[holder]
            if hasattr(self, 'customMembershipCheck'):
                self.customMembershipCheck(fit, holder)

        fit._restrictionTracker.enableStates.side_effect = handleRtEnableStates
        fit._restrictionTracker.disableStates.side_effect = handleRtDisableStates
