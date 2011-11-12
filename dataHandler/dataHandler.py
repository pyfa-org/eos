#===============================================================================
# Copyright (C) 2011 Diego Duclos
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

from abc import ABCMeta
from abc import abstractmethod

class DataHandler(object):
    '''
    DataHandler abstract baseclass, it handles fetching relevant data from wherever it is stored
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def getExpression(self, id):
        ...

    @abstractmethod
    def getType(self, id):
        ...

    @abstractmethod
    def getEffect(self, id):
        ...
