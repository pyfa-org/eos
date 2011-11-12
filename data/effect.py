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

class Effect(object):
    '''
    Represents a single effect. Effects are the building blocks of types and are what actualy make a type do something.
    In turn, each effect is made out of pre- and a post-expression
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''

    def __init__(self, id, preExpression, postExpression, isOffensive, isAssistance):
        self.id = id
        self.preExpression = preExpression
        self.postExpression = postExpression
        self.isOffensive = isOffensive
        self.isAssistance = isAssistance
