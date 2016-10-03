# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from unittest.mock import patch

from eos.fit import Fit
from tests.eos_testcase import EosTestCase


class FitTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assert_object_buffers_empty -- checks if fit has
    any holders assigned to it.
    self.make_fit -- create fit with all services replaced
    by mocks. Everything added to link tracker is stored in
    fit.lt in {holder: {enabled states}} format, everything
    added to restriction tracker is stored in fit.rt in
    {holder: {enabled states}} format. If any specific
    membership checks need to be performed upon holder
    addition to and removal from trackers, they can be
    specified in custom_membership_check(fit, holder) of
    child classes.
    """

    def assert_fit_buffers_empty(self, fit):
        holder_num = 0
        # Check if we have anything in our single holder  storages
        single_holders = ('character', 'ship', 'effect_beacon')
        for attr_name in single_holders:
            holder = getattr(fit, attr_name, None)
            if holder is not None:
                holder_num += 1
        # Seek for multiple holder storages
        for attr_name in dir(fit):
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue
            attr_val = getattr(fit, attr_name)
            try:
                attr_len = len(attr_val)
            except TypeError:
                pass
            else:
                if attr_len > 0: print(attr_name)
                holder_num += attr_len
        if holder_num > 0:
            plu = 'y' if holder_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(holder_num, plu)
            self.fail(msg=msg)

    @patch('eos.fit.fit.StatTracker')
    @patch('eos.fit.fit.RestrictionTracker')
    @patch('eos.fit.fit.LinkTracker')
    def make_fit(self, *args, source=None):
        fit = Fit(source=source)
        fit.character = None
        self.__setup_tracker_memory(fit)
        return fit

    def __setup_tracker_memory(self, fit):
        # Buffer which will keep track of holders added to
        # link tracker
        # Format: {holder: {states}}
        fit.lt = {}

        def handle_lt_add_holder(holder):
            self.assertNotIn(holder, fit.lt)
            fit.lt[holder] = set()
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        def handle_lt_enable_states(holder, states):
            self.assertIn(holder, fit.lt)
            self.assertEqual(len(set(states).intersection(fit.lt[holder])), 0)
            fit.lt[holder].update(set(states))
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        def handle_lt_disable_states(holder, states):
            self.assertIn(holder, fit.lt)
            self.assertEqual(len(set(states).difference(fit.lt[holder])), 0)
            fit.lt[holder].difference_update(set(states))
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        def handle_lt_remove_holder(holder):
            self.assertIn(holder, fit.lt)
            self.assertEqual(len(fit.lt[holder]), 0)
            del fit.lt[holder]
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        fit._link_tracker.add_holder.side_effect = handle_lt_add_holder
        fit._link_tracker.enable_states.side_effect = handle_lt_enable_states
        fit._link_tracker.disable_states.side_effect = handle_lt_disable_states
        fit._link_tracker.remove_holder.side_effect = handle_lt_remove_holder

        # Buffer which will keep track of holders added to
        # restriction tracker
        # Format: {holder: {states}}
        fit.rt = {}

        def handle_rt_enable_states(holder, states):
            if holder not in fit.rt:
                fit.rt[holder] = set()
            self.assertEqual(len(set(states).intersection(fit.rt[holder])), 0)
            fit.rt[holder].update(set(states))
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        def handle_rt_disable_states(holder, states):
            self.assertIn(holder, fit.rt)
            self.assertEqual(len(set(states).difference(fit.rt[holder])), 0)
            fit.rt[holder].difference_update(set(states))
            if len(fit.rt[holder]) == 0:
                del fit.rt[holder]
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        fit._restriction_tracker.enable_states.side_effect = handle_rt_enable_states
        fit._restriction_tracker.disable_states.side_effect = handle_rt_disable_states

        # Buffer which will keep track of holders added to
        # stats tracker
        # Format: {holder: {states}}
        fit.st = {}

        def handle_st_enable_states(holder, states):
            if holder not in fit.st:
                fit.st[holder] = set()
            self.assertEqual(len(set(states).intersection(fit.st[holder])), 0)
            fit.st[holder].update(set(states))
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        def handle_st_disable_states(holder, states):
            self.assertIn(holder, fit.st)
            self.assertEqual(len(set(states).difference(fit.st[holder])), 0)
            fit.st[holder].difference_update(set(states))
            if len(fit.st[holder]) == 0:
                del fit.st[holder]
            if hasattr(self, 'custom_membership_check'):
                self.custom_membership_check(fit, holder)

        fit.stats._enable_states.side_effect = handle_st_enable_states
        fit.stats._disable_states.side_effect = handle_st_disable_states
