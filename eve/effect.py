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

from eos import const
from eos.calc.info.builder.builder import InfoBuilder

class Effect:
    """
    Represents a single effect. Effects are the building blocks of types and are what actualy make a type do something.
    In turn, each effect is made out of pre- and a post-expression
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    """

    def __init__(self, id, preExpression, postExpression, isOffensive, isAssistance):
        # The unique ID of an effect. Can be anything, as long as its unique,
        # typically, the IDs CCP assigned to them in the SDD are used
        self.id = id

        # PreExpression of the effect. A preExpression is the expression
        # that gets run when the module is activated
        self.preExpression = preExpression

        # PostExpression of the effect. A postExpression gets run when the module gets disabled.
        self.postExpression = postExpression

        # Whether the module is offensive (e.g. guns)
        self.isOffensive = isOffensive

        # Whether the module is helpful (e.g. Remote reps)
        self.isAssistance = isAssistance

        # Stores EffectInfos which are assigned to given effect
        self.__infos = None

        # Stores parsing status of info objects
        self.infoStatus = const.effectInfoNotParsed

    @property
    def infos(self):
        """Return a set of all infos this effect contains"""
        if self.__infos is None:
            self.__infos, self.infoStatus = InfoBuilder().build(self.preExpression, self.postExpression)
        return self.__infos

