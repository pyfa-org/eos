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


import os.path
from logging import getLogger, FileHandler, Formatter, INFO

from .abc import BaseLogger


class EosLogger(BaseLogger):
    """
    Handles everything related to logs.

    Required arguments:
    name -- name of root logger for this instance,
    used in log filename
    logFolder -- path to folder for logs
    """

    def __init__(self, name, log_folder):
        self.__setup(name, log_folder)
        # Storage for signatures of logged entries,
        # to avoid logging them again when it's not desirable
        self.__known_signatures = set()

    def info(self, msg, child_name=None, signature=None):
        """
        Log info-level message.

        Required arguments:
        msg -- message to log

        Optional arguments:
        child_name -- name of child logger to use, if None,
        root logger is used (default None)
        signature -- hashable signature of log entry;
        if not None, logger logs message only if no message
        with same signature has been logged during current
        session (default None)
        """
        logger = self.__get_logger(child_name)
        if signature is None:
            logger.info(msg)
        elif signature not in self.__known_signatures:
            logger.info(msg)
            self.__known_signatures.add(signature)

    def warning(self, msg, child_name=None, signature=None):
        """
        Log warning-level message.

        Required arguments:
        msg -- message to log

        Optional arguments:
        child_name -- name of child logger to use, if None,
        root logger is used (default None)
        signature -- hashable signature of log entry;
        if not None, logger logs message only if no message
        with same signature has been logged during current
        session (default None)
        """
        logger = self.__get_logger(child_name)
        if signature is None:
            logger.warning(msg)
        elif signature not in self.__known_signatures:
            logger.warning(msg)
            self.__known_signatures.add(signature)

    def error(self, msg, child_name=None, signature=None):
        """
        Log error-level message.

        Required arguments:
        msg -- message to log

        Optional arguments:
        child -- name of child logger to use, if None,
        root logger is used (default None)
        signature -- hashable signature of log entry;
        if not None, logger logs message only if no message
        with same signature has been logged during current
        session (default None)
        """
        logger = self.__get_logger(child_name)
        if signature is None:
            logger.error(msg)
        elif signature not in self.__known_signatures:
            logger.error(msg)
            self.__known_signatures.add(signature)

    def __setup(self, name, log_folder):
        """
        Configure python logging system for our neeeds.

        Required arguments:
        name -- name of root python logger which will be
        used as root for our logger object
        log_folder -- path to folder for logs
        """
        self.__root_logger = getLogger(name)
        # Set level to INFO to enable handling of
        # all messages with level up to info
        self.__root_logger.setLevel(INFO)
        # Clear any handlers this logger already may have
        for handler in self.__root_logger.handlers:
            self.__root_logger.removeHandler(handler)
        # Define log storage options
        if os.path.isdir(log_folder) is not True:
            os.makedirs(log_folder, mode=0o755)
        log_path = os.path.join(log_folder, '{}.log'.format(name))
        handler = FileHandler(log_path, mode='a', encoding='utf-8', delay=False)
        # Set up formatter options
        msg_format = '{asctime:19.19} | {levelname:7.7} | {name:23.23} | {message}'
        time_format = '%Y-%m-%d %H:%M:%S'  # Must be specified in old style, as of python 3.2
        formatter = Formatter(fmt=msg_format, datefmt=time_format, style='{')
        handler.setFormatter(formatter)
        self.__root_logger.addHandler(handler)

    def __get_logger(self, child_name=None):
        """
        Get python's logger instance, which may be used to log
        actual entries according to logging module documentation.

        Optional arguments:
        child_name -- name of child logger to get, if None is
        passed, root logger is returned (default None)
        """
        if child_name is None:
            logger = self.__root_logger
        else:
            logger = self.__root_logger.getChild(child_name)
        return logger
