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


class Info:
    """
    Info objects are eos-specific abstraction, they replace effects
    (with the very few exceptions). Each info object contains full
    description of modification: when it should be applied, on which
    items, under which conditions, and so on.
    """

    def __init__(self):
        # Conditions under which modification is applied,
        # must be None or tree of condition Atom objects.
        self.conditions = None

        # Info can be applied only when its holder is in
        # this or greater state, must be State class'
        # attribute value.
        self.state = None

        # Describes context in which info is applied, must
        # be Context class' attribute value.
        self.context = None

        # Time context in which modification is applied, must
        # be eos.const.RunTime class' attribute value.
        self.runTime = None

        # Target location to change, must be eos.const.Location
        # class' attribute value.
        self.location = None

        # Filter type of the modification, must be None or
        # eos.const.FilterType class' attribute value.
        self.filterType = None

        # Filter value of the modification:
        # For filterType.all or filterType.None must be None;
        # For filterType.group must be some integer, referring group via ID;
        # For filterType.skill must be some integer, referring type via ID,
        # or eos.const.InvType.self_ to reference type of info carrier.
        self.filterValue = None

        # Which operation should be applied during modification,
        # must be eos.const.Operator class' attribute value.
        self.operator = None

        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.targetAttributeId = None

        # SourceValue type, must be eos.const.SourceType class'
        # attribute value.
        self.sourceType = None

        # Value which is used as modification value for operation:
        # For sourceType.attribute must be integer which refers attribute via ID;
        # For sourceType.value must be any value CCP can define in expression, integer or value.
        self.sourceValue = None
