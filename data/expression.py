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

class Expression:
    """
    Expression class. Each effect is made out of several expressions. Which in turn, can be made out of expressions themselves.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it.
    All info in this object is taken straight from EVE's cache.
    """

    def __init__(self, id, operand, value=None, arg1=None, arg2=None,
                 typeId=None, groupId=None, attributeId=None):
        self.id = id
        self.operand = operand
        self.value = value
        self.arg1 = arg1
        self.arg2 = arg2
        self.typeId = typeId
        self.groupId = groupId
        self.attributeId = attributeId
