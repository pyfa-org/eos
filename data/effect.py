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
class Effect(object):
    '''
    Represents a single effect. Effects are the building blocks of types and are what actualy make a type do something.
    In turn, each effect is made out of pre- and a post-expression
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''

    def __init__(self, dataHandler, id, preExpression, postExpression, isOffensive, isAssistance):
        self.dataHandler = dataHandler
        self.id = id
        self.preExpression = preExpression
        self.postExpression = postExpression
        self.isOffensive = isOffensive
        self.isAssistance = isAssistance