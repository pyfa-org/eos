'''
Created on 11-nov.-2011

@author: cncfanatics

This file is part of eos.

eos is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Eos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with eos.  If not, see <http://www.gnu.org/licenses/>.
'''
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