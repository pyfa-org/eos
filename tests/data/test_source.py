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


import pytest

from eos import SourceManager
from eos.data.source import Source
from eos.data.exception import ExistingSourceError, UnknownSourceError
from unittest.mock import MagicMock, Mock


@pytest.fixture
def mock_data_handler():
    data_handler = MagicMock()
    return data_handler


@pytest.fixture
def mock_cache_handler():
    cache_handler = MagicMock()
    return cache_handler


def setup_function():
    SourceManager._sources = {}
    SourceManager.default = None


def teardown_function():
    SourceManager._sources = {}
    SourceManager.default = None


def test_add_existing_source_error(mock_data_handler, mock_cache_handler):
    SourceManager.add('test', mock_data_handler, mock_cache_handler, True)

    with pytest.raises(ExistingSourceError):
        SourceManager.add('test', mock_data_handler, mock_cache_handler, True)


def test_add_sets_sources(mock_data_handler, mock_cache_handler):
    alias = 'test'
    source = Source(alias=alias, cache_handler=mock_cache_handler)

    SourceManager.add(alias, mock_data_handler, mock_cache_handler, True)

    assert SourceManager._sources == {alias: source}
    assert SourceManager.default == source


def test_add_does_not_set_default(mock_data_handler, mock_cache_handler):
    SourceManager.add('test', mock_data_handler, mock_cache_handler)

    assert SourceManager.default is None


def test_add_processes_with_data_version_none(mock_data_handler, mock_cache_handler, caplog):
    mock_data_handler.get_version = Mock(return_value=None)
    SourceManager.add('test', mock_data_handler, mock_cache_handler)

    assert mock_cache_handler.update_cache.called
    assert 'data version is None, updating cache' in caplog.text()


def test_add_fingerprint_mismatch(mock_data_handler, mock_cache_handler, caplog):
    mock_cache_handler.get_fingerprint = Mock(return_value='cache_fingerprint')
    mock_data_handler.get_version = Mock(return_value='dh_version')
    SourceManager.add('test', mock_data_handler, mock_cache_handler)

    log_msg = 'fingerprint mismatch: cache "cache_fingerprint", data "dh_version_0.0.0.dev8", updating cache'

    assert log_msg in caplog.text()


def test_removing_known_source(mock_data_handler, mock_cache_handler):
    SourceManager.add('test', mock_data_handler, mock_cache_handler)
    SourceManager.remove('test')

    assert 'test' not in SourceManager._sources


def test_removing_unknown_source(mock_data_handler, mock_cache_handler):
    with pytest.raises(UnknownSourceError):
        SourceManager.remove('test')


def test_get_real_source(mock_data_handler, mock_cache_handler):
    alias = 'test'
    source = Source(alias=alias, cache_handler=mock_cache_handler)

    SourceManager.add(alias, mock_data_handler, mock_cache_handler)
    result = SourceManager.get(alias)

    assert result == source


def test_get_unkown_source(mock_data_handler, mock_cache_handler):
    with pytest.raises(UnknownSourceError):
        SourceManager.get('test')


def test_list_sources_correctly(mock_data_handler, mock_cache_handler):
    SourceManager.add('source one', mock_data_handler, mock_cache_handler)
    SourceManager.add('source two', mock_data_handler, mock_cache_handler)
    SourceManager.add('source three', mock_data_handler, mock_cache_handler)

    sources = SourceManager.list()

    assert sorted(sources) == sorted(['source one', 'source two', 'source three'])
