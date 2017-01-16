# ===============================================================================
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
# ===============================================================================


from unittest.mock import Mock, patch

from eos.data.source import Source
from eos.fit.messages import HolderAdded, HolderRemoved, EnableServices, DisableServices, RefreshSource
from tests.fit.environment import Fit, Holder
from tests.fit.fit_testcase import FitTestCase


@patch('eos.fit.fit.SourceManager')
class FitSourceSwitch(FitTestCase):

    def test_none_to_none(self, source_mgr):
        source_mgr.default = None
        holder = Holder()
        fit = Fit(source=None)
        fit._publish(HolderAdded(holder))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = None
        # Checks
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_none_to_source(self, source_mgr):
        source_mgr.default = None
        source = Mock(spec_set=Source)
        holder = Holder()
        assertions = {
            RefreshSource: lambda f: self.assertIs(f.source, source),
            EnableServices: lambda f: self.assertIs(f.source, source)
        }
        fit = Fit(source=None, message_assertions=assertions)
        fit._publish(HolderAdded(holder))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = source
        # Checks
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = fit.message_store[-2]
        self.assertTrue(isinstance(message1, RefreshSource))
        message2 = fit.message_store[-1]
        self.assertTrue(isinstance(message2, EnableServices))
        self.assertEqual(message2.holders, {holder})
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_source_to_none(self, source_mgr):
        source_mgr.default = None
        source = Mock(spec_set=Source)
        holder = Holder()
        assertions = {
            DisableServices: lambda f: self.assertIs(f.source, source),
            RefreshSource: lambda f: self.assertIsNone(f.source)
        }
        fit = Fit(source=source, message_assertions=assertions)
        fit._publish(HolderAdded(holder))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = None
        # Checks
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = fit.message_store[-2]
        self.assertTrue(isinstance(message1, DisableServices))
        self.assertEqual(message1.holders, {holder})
        message2 = fit.message_store[-1]
        self.assertTrue(isinstance(message2, RefreshSource))
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_source_to_source(self, source_mgr):
        source_mgr.default = None
        source1 = Mock(spec_set=Source)
        source2 = Mock(spec_set=Source)
        holder = Holder()
        assertions = {
            DisableServices: lambda f: self.assertIs(f.source, source1),
            RefreshSource: lambda f: self.assertIs(f.source, source2),
            EnableServices: lambda f: self.assertIs(f.source, source2)
        }
        fit = Fit(source=source1, message_assertions=assertions)
        fit._publish(HolderAdded(holder))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = source2
        # Checks
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 3)
        message1 = fit.message_store[-3]
        self.assertTrue(isinstance(message1, DisableServices))
        self.assertEqual(message1.holders, {holder})
        message2 = fit.message_store[-2]
        self.assertTrue(isinstance(message2, RefreshSource))
        message3 = fit.message_store[-1]
        self.assertTrue(isinstance(message3, EnableServices))
        self.assertEqual(message3.holders, {holder})
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_source_to_source_same(self, source_mgr):
        source_mgr.default = None
        source = Mock(spec_set=Source)
        holder = Holder()
        fit = Fit(source=source)
        fit._publish(HolderAdded(holder))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = source
        # Checks
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_none_to_literal_source(self, source_mgr):
        source = Mock(spec_set=Source)
        source_mgr.get.side_effect = lambda alias: source if alias == 'src_alias' else None
        source_mgr.default = None
        holder = Holder()
        assertions = {
            RefreshSource: lambda f: self.assertIs(f.source, source),
            EnableServices: lambda f: self.assertIs(f.source, source)
        }
        fit = Fit(source=None, message_assertions=assertions)
        fit._publish(HolderAdded(holder))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = 'src_alias'
        # Checks
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = fit.message_store[-2]
        self.assertTrue(isinstance(message1, RefreshSource))
        message2 = fit.message_store[-1]
        self.assertTrue(isinstance(message2, EnableServices))
        self.assertEqual(message2.holders, {holder})
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)
