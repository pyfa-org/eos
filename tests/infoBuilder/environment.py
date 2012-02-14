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


"""
This file contains helper classes, which implement minimalistic
version of environment in which attributeCalculator resides.
"""


from logging import getLogger


class Logger:
    def __init__(self):
        self.__knownSignatures = set()

    def warning(self, msg, child=None, signature=None):
        if child is None:
            logger = getLogger("eos_test")
        else:
            logger = getLogger("eos_test").getChild(child)
        if signature is None:
            logger.warning(msg)
        elif not signature in self.__knownSignatures:
            logger.warning(msg)
            self.__knownSignatures.add(signature)
