#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


class Modifier:
    """
    Modifier objects are Eos-specific abstraction, they replace effects'
    expressions. Each modifier object contains full description of
    modification: when it should be applied, on which items, how to
    apply it, and so on.
    """

    def __init__(self, modifierId=None, state=None, context=None,
                 sourceAttributeId=None, operator=None, targetAttributeId=None,
                 location=None, filterType=None, filterValue=None):
        # Identifier of modifier, sythesized at
        # cache generation time
        self.id = modifierId

        # Modifier can be applied only when its carrier holder
        # is in this or greater state, must be eos.const.eos.State
        # class' attribute value.
        self.state = state

        # Describes context in which modifier is applied, must
        # be eos.const.eos.Context class' attribute value.
        self.context = context

        # Which attribute will be taken as source value,
        # must be integer which refers attribute via ID.
        self.sourceAttributeId = sourceAttributeId

        # Which operation should be applied during modification,
        # must be eos.const.eos.Operator class' attribute value.
        self.operator = operator

        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.targetAttributeId = targetAttributeId

        # Target location to change, must be eos.const.eos.Location
        # class' attribute value.
        self.location = location

        # Filter type of the modification, must be None or
        # eos.const.eos.FilterType class' attribute value.
        self.filterType = filterType

        # Filter value of the modification:
        # For filterType.all_, filterType.None or filterType.skillSelf must be None;
        # For filterType.group must be some integer, referring group via ID;
        # For filterType.skill must be some integer, referring type via ID
        self.filterValue = filterValue
