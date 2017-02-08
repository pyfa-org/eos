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
from eos.fit.messages import ItemAdded, ItemRemoved, EnableServices, DisableServices, RefreshSource
from eos.fit.null_source import NullSourceItem
from tests.fit.environment import Fit, Item
from tests.fit.fit_testcase import FitTestCase


@patch('eos.fit.fit.SourceManager')
class FitSourceSwitch(FitTestCase):

    def make_source(self):
        source = Mock(spec_set=Source)
        source.cache_handler.get_type.return_value = NullSourceItem
        return source

    def test_none_to_none(self, source_mgr):
        source_mgr.default = None
        item = Item()
        fit = Fit(source=None)
        fit._publish(ItemAdded(item))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = None
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_none_to_source(self, source_mgr):
        source_mgr.default = None
        source = self.make_source()
        item = Item()
        assertions = {
            RefreshSource: lambda f: self.assertIs(f.source, source),
            EnableServices: lambda f: self.assertIs(f.source, source)
        }
        fit = Fit(source=None, message_assertions=assertions)
        fit._publish(ItemAdded(item))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = source
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = fit.message_store[-2]
        self.assertTrue(isinstance(message1, RefreshSource))
        message2 = fit.message_store[-1]
        self.assertTrue(isinstance(message2, EnableServices))
        self.assertEqual(message2.items, {item})
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_source_to_none(self, source_mgr):
        source_mgr.default = None
        source = self.make_source()
        item = Item()
        assertions = {
            DisableServices: lambda f: self.assertIs(f.source, source),
            RefreshSource: lambda f: self.assertIsNone(f.source)
        }
        fit = Fit(source=source, message_assertions=assertions)
        fit._publish(ItemAdded(item))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = None
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = fit.message_store[-2]
        self.assertTrue(isinstance(message1, DisableServices))
        self.assertEqual(message1.items, {item})
        message2 = fit.message_store[-1]
        self.assertTrue(isinstance(message2, RefreshSource))
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_source_to_source(self, source_mgr):
        source_mgr.default = None
        source1 = self.make_source()
        source2 = self.make_source()
        item = Item()
        assertions = {
            DisableServices: lambda f: self.assertIs(f.source, source1),
            RefreshSource: lambda f: self.assertIs(f.source, source2),
            EnableServices: lambda f: self.assertIs(f.source, source2)
        }
        fit = Fit(source=source1, message_assertions=assertions)
        fit._publish(ItemAdded(item))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = source2
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 3)
        message1 = fit.message_store[-3]
        self.assertTrue(isinstance(message1, DisableServices))
        self.assertEqual(message1.items, {item})
        message2 = fit.message_store[-2]
        self.assertTrue(isinstance(message2, RefreshSource))
        message3 = fit.message_store[-1]
        self.assertTrue(isinstance(message3, EnableServices))
        self.assertEqual(message3.items, {item})
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_source_to_source_same(self, source_mgr):
        source_mgr.default = None
        source = self.make_source()
        item = Item()
        fit = Fit(source=source)
        fit._publish(ItemAdded(item))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = source
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_none_to_literal_source(self, source_mgr):
        source = self.make_source()
        source_mgr.get.side_effect = lambda alias: source if alias == 'src_alias' else None
        source_mgr.default = None
        item = Item()
        assertions = {
            RefreshSource: lambda f: self.assertIs(f.source, source),
            EnableServices: lambda f: self.assertIs(f.source, source)
        }
        fit = Fit(source=None, message_assertions=assertions)
        fit._publish(ItemAdded(item))
        messages_before = len(fit.message_store)
        # Action
        with self.fit_assertions(fit):
            fit.source = 'src_alias'
        # Verification
        messages_after = len(fit.message_store)
        self.assertEqual(messages_after - messages_before, 2)
        message1 = fit.message_store[-2]
        self.assertTrue(isinstance(message1, RefreshSource))
        message2 = fit.message_store[-1]
        self.assertTrue(isinstance(message2, EnableServices))
        self.assertEqual(message2.items, {item})
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)
