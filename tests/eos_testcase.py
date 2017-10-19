# ==============================================================================
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
# ==============================================================================


from collections.abc import Iterable
from copy import deepcopy
from fnmatch import fnmatchcase
from logging import getLogger, DEBUG
from logging.handlers import BufferingHandler
from unittest import TestCase
from unittest.mock import DEFAULT

from .environment import CacheHandler


class TestLogHandler(BufferingHandler):
    """Custom logging handler class for testing.

    Sends no data into external sinks.
    """
    def __init__(self):
        # Capacity is zero, as we won't rely on it when deciding when to flush
        # data
        BufferingHandler.__init__(self, 0)

    def shouldFlush(self, *args):
        return False

    def emit(self, record):
        self.buffer.append(record)


class EosTestCase(TestCase):
    """Test case class is used by all eos tests.

    Attributes:
        ch: Default cache handler.
    """

    def setUp(self):
        """Set up environment for tests.

        When redefining this method in child classes, make sure to call it
        before child's setup has started.
        """
        super().setUp()
        logger = getLogger()
        # Save existing data about logging system (log level and handlers)
        self.__backup_loglevel = logger.getEffectiveLevel()
        logger.setLevel(DEBUG)
        self.__backup_log_handlers = []
        for handler in logger.handlers:
            self.__backup_log_handlers.append(handler)
            logger.removeHandler(handler)
        # Place test logger instead of them
        self.__test_log_handler = TestLogHandler()
        logger.addHandler(self.__test_log_handler)
        # Add cache handler to each test case
        self.ch = self._make_cache_handler()

    def tearDown(self):
        """Do clean-up jobs.

        When redefining this method in child classes, make sure to call it after
        child's teardown has been completed.
        """
        # Remove test logger and restore loggers which were removed during setup
        logger = getLogger()
        logger.removeHandler(self.__test_log_handler)
        self.__test_log_handler.close()
        for handler in self.__backup_log_handlers:
            logger.addHandler(handler)
        logger.setLevel(self.__backup_loglevel)

    def get_log(self, name=None):
        """Get entries which were logged during the test.

        Args:
            name (optional): If specified, only entries logged by logger with
                this name will be returned. Supports wildcards. By default, all
                entries are returned.

        Returns:
            List with log entries.
        """
        log = []
        for log_entry in self.__test_log_handler.buffer:
            if name is None or fnmatchcase(log_entry.name, name):
                log.append(log_entry)
        return log

    def _make_cache_handler(self):
        return CacheHandler()

    def assert_object_buffers_empty(
            self, object_, ignore_objects=(), ignore_attrs=()):
        """Checks if buffers of passed object are clear.

        Fails test if there's something remaining in buffers. Useful to detect
        memory leaks.

        Args:
            object_: Object to check.
            ignore_objects (optional): Iterable with objects which should be
                ignored during check.
            ignore_attrs: Iterable with attribute names which should be ignored
                during check.
        """
        entry_num = self._get_object_buffer_entry_amount(
            object_, ignore_objects, ignore_attrs)
        # Raise error if we found any data in any attached storage
        if entry_num:
            plu = 'y' if entry_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(
                entry_num, plu)
            self.fail(msg=msg)

    def _get_object_buffer_entry_amount(
            self, object_, ignore_objects=(), ignore_attrs=(),
            checked_objects=None):
        entry_amt = 0
        # Initialize variables for initial call
        if checked_objects is None:
            checked_objects = set()
        # Fetch attributes of the passed instance and check all of them
        try:
            object_vars = tuple(vars(object_).items())
        # If we cannot get attributes of an instance, try just iterating over it
        except TypeError:
            # Anything iterable but string
            if isinstance(object_, Iterable) and not isinstance(object_, str):
                object_vars = []
                # Get list of values this object exposes through iteration
                available_values = list(value for value in object_)
                # Try to find names for them and put named attribs to the list
                for attr_name in dir(object_):
                    attr_value = getattr(object_, attr_name)
                    if attr_value not in available_values:
                        continue
                    object_vars.append((attr_name, attr_value))
                    available_values.remove(attr_value)
                # For values without names, use None as name
                for remaining_value in available_values:
                    object_vars.append((None, remaining_value))
            # Do nothing if we have no idea what to do with object attribs
            else:
                return entry_amt
        obj_classname = type(object_).__name__
        for attr_name, attr_val in object_vars:
            # Skip internal python attributes
            if (
                attr_name is not None and
                attr_name.startswith('__') and
                attr_name.endswith('__')
            ):
                continue
            # Skip attributes with values we've already investigated
            if id(attr_val) in checked_objects:
                continue
            # Skip attributes with names we should ignore
            if (obj_classname, attr_name) in ignore_attrs:
                continue
            # Skip attributes with values we should ignore
            if attr_val in ignore_objects:
                continue
            # From here we consider that we're checking this attribute
            checked_objects.add(id(attr_val))
            # Ignore strings, as Eos doesn't deal with them - they are mostly
            # used to refer various attributes and are stored on object
            # permanently
            if isinstance(attr_val, str):
                continue
            try:
                attr_len = len(attr_val)
            except TypeError:
                pass
            else:
                entry_amt += attr_len
            # Recursively check children if value we're checking is defined
            # within eos
            attr_val_module = type(attr_val).__module__
            if (
                attr_val_module == 'eos' or
                attr_val_module.startswith('eos.') or
                isinstance(attr_val, Iterable)
            ):
                entry_amt += self._get_object_buffer_entry_amount(
                    attr_val, ignore_objects=ignore_objects,
                    ignore_attrs=ignore_attrs, checked_objects=checked_objects)
        return entry_amt

    def _setup_args_capture(self, mock_obj, arg_list):
        """Capture all arguments passed to mock into list.

        In case when we want to capture exact state of arguments passed to mock
        (to verify what they looked like, if they were further modified by
        object under test), we have to copy them at the time they were passed to
        mock. This method assists with this, it takes passed mock and records
        copies of all passed arguments into list passed as second argument in
        the form of tuple (args, kwargs).
        """

        def capture_args(*args, **kwargs):
            arg_list.append((deepcopy(args), deepcopy(kwargs)))
            return DEFAULT

        mock_obj.side_effect = capture_args
