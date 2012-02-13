#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
from logging import getLogger, FileHandler, Formatter


class Logger:
    """
    Handles everything related to logs.

    Positional arguments:
    name -- name of root logger for this instance,
    used in log filename
    """
    def __init__(self, name):
        self.__setup(name)
        # Storage for signatures of logged entries,
        # to avoid logging them again when it's not desirable
        self.__knownSignatures = set()

    def warning(self, msg, child=None, signature=None):
        """
        Log warning-level message.

        Positional arguments:
        msg -- message to log

        Keyword arguments:
        child -- name of child logger to use, if None,
        root logger is used (default None)
        signature -- hashable signature of log entry;
        if not None, logger logs message only if no message
        with same signature has been logged during current
        session (default None)
        """
        logger = self.__getLogger(child)
        if signature is None:
            logger.warning(msg)
        elif not signature in self.__knownSignatures:
            logger.warning(msg)
            self.__knownSignatures.add(signature)

    def __setup(self, name):
        """
        Configure python logging system for our neeeds.

        Positional arguments:
        name -- name of root python logger which will be
        used as root for our logger object
        """
        self.__rootLogger = getLogger(name)
        # Clear any handlers this logger already may have
        for handler in self.__rootLogger.handlers:
            self.__rootLogger.removeHandler(handler)
        # Define how logger will handle log entries
        logPath = os.path.expanduser(os.path.join("~", "Desktop", "eos_logs", "{}.log".format(name)))
        handler = FileHandler(logPath, mode="a", encoding="utf-8", delay=False)
        formatter = Formatter(fmt="{asctime}: {message}", style="{")
        handler.setFormatter(formatter)
        self.__rootLogger.addHandler(handler)

    def __getLogger(self, name=None):
        """
        Get python's logger instance, which may be used to log
        actual entries according to logging module documentation.

        Keyword arguments:
        name -- name of child logger to get, if None is passed,
        root logger is returned (default None)
        """
        if name is None:
            logger = self.__rootLogger
        else:
            logger = self.__rootLogger.getChild(name)
        return logger
