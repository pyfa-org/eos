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


import logging
import os.path


def setup():
    logger = logging.getLogger("eos")
    logPath = os.path.expanduser(os.path.join("~", "Desktop", "eoslog"))
    handler = logging.FileHandler(logPath, mode="a", encoding="utf-8", delay=False)
    formatter = logging.Formatter(fmt="{asctime}: {message}", style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
