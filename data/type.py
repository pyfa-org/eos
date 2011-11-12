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

class Type(object):
    '''
    A type, the basic building blocks of EVE. Everything that can do something is a type.
    Each type is built out of several effects and attributes.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''

    def __init__(self, dataHandler, id, groupId, effects, attributes):
        self.dataHandler = dataHandler
        self.id = id
        self.groupId = groupId
        self.effects = effects
        self.attributes = attributes
