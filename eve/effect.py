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


from eos.calc.info.builder.builder import InfoBuilder, InfoBuildStatus


class Effect:
    """
    Represents a single effect. Effects are the building blocks which describe what its carrier
    does with other items.
    """

    def __init__(self, id_, categoryId=None, isOffensive=None, isAssistance=None,
                 preExpression=None, postExpression=None):
        # The unique ID of an effect
        self.id = int(id_) if id_ is not None else None

        # Effect category actually describes type of effect, which determines
        # when it is applied - always, when item is active, overloaded, etc.
        self.categoryId = int(categoryId) if categoryId is not None else None

        # Whether the effect is offensive (e.g. guns)
        self.isOffensive = bool(isOffensive) if isOffensive is not None else None

        # Whether the effect is helpful (e.g. remote repairers)
        self.isAssistance = bool(isAssistance) if isAssistance is not None else None

        # PreExpression of the effect. A preExpression is the expression
        # that gets run when the module is activated
        self.preExpression = preExpression

        # PostExpression of the effect. A postExpression gets run when the module gets disabled.
        self.postExpression = postExpression

        # Stores EffectInfos which are assigned to given effect
        self.__infos = None

        # Stores parsing status of info objects
        self.infoStatus = InfoBuildStatus.notParsed

    def getInfos(self):
        """Return a set of all infos this effect contains"""
        if self.__infos is None:
            self.__infos, self.infoStatus = InfoBuilder().build(self.preExpression, self.postExpression, self.categoryId)
        return self.__infos
