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


from unittest.mock import Mock, call

from eos.const.eos import State
from eos.fit.holder.item import ModuleHigh
from tests.stat_tracker.stat_testcase import StatTestCase


class TestStatsDamageVolley(StatTestCase):

    def test_empty(self):
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertAlmostEqual(stats_volley.thermal, 2.3)
        self.assertAlmostEqual(stats_volley.kinetic, 3.4)
        self.assertAlmostEqual(stats_volley.explosive, 4.5)
        self.assertAlmostEqual(stats_volley.total, 11.4)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_multiple(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder1 = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        holder2 = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        holder1_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder2_volley = Mock(em=0, thermal=4, kinetic=2, explosive=7.1, total=99)
        holder1.get_nominal_volley.return_value = holder1_volley
        holder2.get_nominal_volley.return_value = holder2_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertAlmostEqual(stats_volley.thermal, 6.3)
        self.assertAlmostEqual(stats_volley.kinetic, 5.4)
        self.assertAlmostEqual(stats_volley.explosive, 11.6)
        self.assertAlmostEqual(stats_volley.total, 24.5)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_not_damage_dealer(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item)
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_arguments_custom(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        arg_resistances = Mock()
        calls_before = len(holder.get_nominal_volley.mock_calls)
        self.st.get_nominal_volley(target_resistances=arg_resistances)
        calls_after = len(holder.get_nominal_volley.mock_calls)
        self.assertEqual(calls_after - calls_before, 1)
        self.assertEqual(holder.get_nominal_volley.mock_calls[-1], call(target_resistances=arg_resistances))
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_arguments_default(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        calls_before = len(holder.get_nominal_volley.mock_calls)
        self.st.get_nominal_volley()
        calls_after = len(holder.get_nominal_volley.mock_calls)
        self.assertEqual(calls_after - calls_before, 1)
        self.assertEqual(holder.get_nominal_volley.mock_calls[-1], call(target_resistances=None))
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_none_em(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=None, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertAlmostEqual(stats_volley.thermal, 2.3)
        self.assertAlmostEqual(stats_volley.kinetic, 3.4)
        self.assertAlmostEqual(stats_volley.explosive, 4.5)
        self.assertAlmostEqual(stats_volley.total, 10.2)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_none_therm(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=None, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertIsNone(stats_volley.thermal)
        self.assertAlmostEqual(stats_volley.kinetic, 3.4)
        self.assertAlmostEqual(stats_volley.explosive, 4.5)
        self.assertAlmostEqual(stats_volley.total, 9.1)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_none_kin(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=None, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertAlmostEqual(stats_volley.thermal, 2.3)
        self.assertIsNone(stats_volley.kinetic)
        self.assertAlmostEqual(stats_volley.explosive, 4.5)
        self.assertAlmostEqual(stats_volley.total, 8)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_none_expl(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=None, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertAlmostEqual(stats_volley.thermal, 2.3)
        self.assertAlmostEqual(stats_volley.kinetic, 3.4)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 6.9)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_none_all(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=None, thermal=None, kinetic=None, explosive=None, total=None)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_zero_em(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=0, thermal=None, kinetic=None, explosive=None, total=None)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 0)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_zero_therm(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=None, thermal=0, kinetic=None, explosive=None, total=None)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertAlmostEqual(stats_volley.thermal, 0)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_zero_kin(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=None, thermal=None, kinetic=0, explosive=None, total=None)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertAlmostEqual(stats_volley.kinetic, 0)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_single_zero_expl(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=None, thermal=None, kinetic=None, explosive=0, total=None)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertAlmostEqual(stats_volley.explosive, 0)
        self.assertAlmostEqual(stats_volley.total, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_none_and_data(self):
        # As container for damage dealers is not ordered,
        # this test may be unreliable (even if there's issue,
        # it won't fail each run)
        item = self.ch.type_(type_id=1, attributes={})
        holder1 = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        holder2 = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        holder1_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder2_volley = Mock(em=None, thermal=None, kinetic=None, explosive=None, total=None)
        holder1.get_nominal_volley.return_value = holder1_volley
        holder2.get_nominal_volley.return_value = holder2_volley
        stats_volley = self.st.get_nominal_volley()
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertAlmostEqual(stats_volley.thermal, 2.3)
        self.assertAlmostEqual(stats_volley.kinetic, 3.4)
        self.assertAlmostEqual(stats_volley.explosive, 4.5)
        self.assertAlmostEqual(stats_volley.total, 11.4)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_filter_success(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley(holder_filter=lambda h: True)
        self.assertAlmostEqual(stats_volley.em, 1.2)
        self.assertAlmostEqual(stats_volley.thermal, 2.3)
        self.assertAlmostEqual(stats_volley.kinetic, 3.4)
        self.assertAlmostEqual(stats_volley.explosive, 4.5)
        self.assertAlmostEqual(stats_volley.total, 11.4)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_filter_fail(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder)
        holder_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder.get_nominal_volley.return_value = holder_volley
        stats_volley = self.st.get_nominal_volley(holder_filter=lambda h: False)
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_filter_mixed(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder1 = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        holder2 = Mock(state=State.active, item=item, spec=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        holder1_volley = Mock(em=1.2, thermal=2.3, kinetic=3.4, explosive=4.5, total=5.6)
        holder2_volley = Mock(em=0, thermal=4, kinetic=2, explosive=7.1, total=99)
        holder1.get_nominal_volley.return_value = holder1_volley
        holder2.get_nominal_volley.return_value = holder2_volley
        stats_volley = self.st.get_nominal_volley(holder_filter=lambda h: h is holder2)
        self.assertAlmostEqual(stats_volley.em, 0)
        self.assertAlmostEqual(stats_volley.thermal, 4)
        self.assertAlmostEqual(stats_volley.kinetic, 2)
        self.assertAlmostEqual(stats_volley.explosive, 7.1)
        self.assertAlmostEqual(stats_volley.total, 13.1)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
