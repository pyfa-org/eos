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
from eos.fit.holder.item import Character, EffectBeacon
from eos.tests.fit.fit_testcase import FitTestCase


class TestDirectHolderSystemWide(FitTestCase):

    def custom_membership_check(self, fit, holder):
        self.assertIs(fit.effect_beacon, holder)

    def test_detached_none_to_none(self):
        fit = self.make_fit()
        # Action
        fit.effect_beacon = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.effect_beacon)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_detached_none_to_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=EffectBeacon)
        # Action
        fit.effect_beacon = holder
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(fit.effect_beacon, holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.effect_beacon = None
        self.assert_fit_buffers_empty(fit)

    def test_detached_none_to_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Character)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'effect_beacon', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.effect_beacon)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_detached_none_to_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=EffectBeacon)
        fit_other.effect_beacon = holder
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'effect_beacon', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIsNone(fit.effect_beacon)
        self.assertIs(fit_other.effect_beacon, holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.effect_beacon = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_holder_to_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=EffectBeacon)
        holder2 = Mock(_fit=None, state=State.active, spec_set=EffectBeacon)
        fit.effect_beacon = holder1
        # Action
        fit.effect_beacon = holder2
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(fit.effect_beacon, holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.effect_beacon = None
        self.assert_fit_buffers_empty(fit)

    def test_detached_holder_to_holder_type_failure(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=EffectBeacon)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Character)
        fit.effect_beacon = holder1
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'effect_beacon', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(fit.effect_beacon, holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.effect_beacon = None
        self.assert_fit_buffers_empty(fit)

    def test_detached_holder_to_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=EffectBeacon)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=EffectBeacon)
        fit.effect_beacon = holder1
        fit_other.effect_beacon = holder2
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'effect_beacon', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(fit.effect_beacon, holder1)
        self.assertIs(fit_other.effect_beacon, holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit_other)
        # Misc
        fit.effect_beacon = None
        fit_other.effect_beacon = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_holder_to_none(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=EffectBeacon)
        fit.effect_beacon = holder
        # Action
        fit.effect_beacon = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.effect_beacon)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_none(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        # Action
        fit.effect_beacon = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.effect_beacon)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_holder(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=EffectBeacon)
        # Action
        fit.effect_beacon = holder
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online})
        self.assertIs(fit.effect_beacon, holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.effect_beacon = None
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_holder_type_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=Character)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'effect_beacon', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.effect_beacon)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_holder_value_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=EffectBeacon)
        fit_other.effect_beacon = holder
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'effect_beacon', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder, fit_other.lt)
        self.assertEqual(fit_other.lt[holder], {State.offline})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder, fit_other.rt)
        self.assertEqual(fit_other.rt[holder], {State.offline})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder, fit_other.st)
        self.assertEqual(fit_other.st[holder], {State.offline})
        self.assertIsNone(fit.effect_beacon)
        self.assertIs(fit_other.effect_beacon, holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.effect_beacon = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_holder_to_holder(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=EffectBeacon)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=EffectBeacon)
        fit.effect_beacon = holder1
        # Action
        fit.effect_beacon = holder2
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertIs(fit.effect_beacon, holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.effect_beacon = None
        self.assert_fit_buffers_empty(fit)

    def test_attached_holder_to_holder_type_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=EffectBeacon)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Character)
        fit.effect_beacon = holder1
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'effect_beacon', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertIs(fit.effect_beacon, holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.effect_beacon = None
        self.assert_fit_buffers_empty(fit)

    def test_attached_holder_to_holder_value_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=EffectBeacon)
        holder2 = Mock(_fit=None, state=State.online, spec_set=EffectBeacon)
        fit.effect_beacon = holder1
        fit_other.effect_beacon = holder2
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'effect_beacon', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder2, fit_other.lt)
        self.assertEqual(fit_other.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder2, fit_other.rt)
        self.assertEqual(fit_other.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder2, fit_other.st)
        self.assertEqual(fit_other.st[holder2], {State.offline, State.online})
        self.assertIs(fit.effect_beacon, holder1)
        self.assertIs(fit_other.effect_beacon, holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit_other)
        # Misc
        fit.effect_beacon = None
        fit_other.effect_beacon = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_holder_to_none(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=EffectBeacon)
        fit.effect_beacon = holder
        # Action
        fit.effect_beacon = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.effect_beacon)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
