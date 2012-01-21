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

from eos.const import EffectCategory

class InfoState:
    """Info required state ID holder"""
    offline = 1  # Applied regardless of carrier holder's state
    online = 2  # Applied when carrier holder is at least in online state (i.e., in active and overloaded too)
    active = 3  # Applied when carrier holder is at least online
    overload = 4  # Applied only when carrier holder is overloaded

    @classmethod
    def _effectCategoryToState(cls, effectCategoryId):
        """
        Convert effect category to state.

        Positional arguments:
        effectCategoryId -- effect category ID

        Return value:
        ID of state, which corresponds to passed effect category,
        or None if no corresponding state was found
        """
        # Format: {effect category ID: state ID}
        conversionMap = {EffectCategory.passive: cls.offline,
                         EffectCategory.active: cls.active,
                         EffectCategory.target: cls.active,
                         EffectCategory.online: cls.online,
                         EffectCategory.overload: cls.overload,
                         EffectCategory.system: cls.offline}
        try:
            result = conversionMap[effectCategoryId]
        except KeyError:
            result = None
        return result

    @classmethod
    def _stateDifference(cls, state1, state2):
        """
        Get difference between two states (states which need to be
        toggled to get from one state to another).

        Positional arguments:
        state1 -- ID of first state to compare, can be None
        state2 -- ID of second state to compare, can be None

        Return value:
        Set with state IDs, which need to be enabled/disabled to perform
        state switch
        """
        # If both passed state are the same, no state
        # switch needed
        if state1 == state2:
            return set()
        # Container which keeps all state IDs
        allStates = {cls.offline, cls.online,
                     cls.active, cls.overload}
        # Get all states you need to trigger to get from
        # no state to given state
        states1 = set(filter(lambda state: state <= state1, allStates)) if state1 is not None else None
        states2 = set(filter(lambda state: state <= state2, allStates)) if state2 is not None else None
        # If one of passed states was None (if both were none, empty set should've been
        # returned already), return other states set
        if states1 is None or states2 is None:
            result = states1 or states2
        # If both states were not None, get all states which are present
        # in one set but not in another
        else:
            result = states1.symmetric_difference(states2)
        return result


class InfoContext:
    """Info required context ID holder"""
    local = 1  # Applied to fit-local holders
    gang = 2  # Applied to gang-mates
    projected = 3  # Applied only when holder is projected onto some ship/fit


class InfoRunTime:
    """Info modification type ID holder"""
    duration = 1  # Applies modification over duration
    pre = 2  # Instant modification, applied in the beginning of the cycle
    post = 3  # Instant modification, applied in the end of the cycle


class InfoLocation:
    """Location ID holder"""
    self_ = 1  # Target self, i.e. carrier of modification source
    character = 2  # Target character
    ship = 3  # Target ship
    target = 4  # Target currently locked and selected ship as target
    other = 5  # If used from charge, targets charge's container, is used from container, targets its charge
    area = 6  # No detailed data about this one, according to expressions, it affects everything on grid (the only expression using it is area-of-effect repair, but it's not assigned to any effects)
    space = 7  # Target stuff in space (e.g. your launched drones and missiles); this location is Eos-specific and not taken from EVE

    @classmethod
    def expressionValueToLocation(cls, expressionValue):
        """
        Convert expression value to location.

        Positional arguments:
        expressionValue -- value of expression, which is supposed
        to be textual location identifier

        Return value:
        ID of location, corresponding to passed textual location
        specifier, or None if no corresponding location was found
        """
        # Format: {location name: location ID}
        conversionMap = {"Self": cls.self_,
                         "Char": cls.character,
                         "Ship": cls.ship,
                         "Target": cls.target,
                         "Other": cls.other,
                         "Area": cls.area}
        try:
            result = conversionMap[expressionValue]
        except KeyError:
            result = None
        return result


class InfoFilterType:
    """Info filter type ID holder"""
    all_ = 1  # Affects all items in target location
    group = 2  # Affects items in target location with additional filter by group
    skill = 3  # Affects items in target location with additional filter by skill requirement


class InfoOperator:
    """Info operator ID holder"""
    # Following operators are used in modifications
    # applied over some duration. We can deliberately assign
    # these some ID, but we need to make sure they're sorted
    # in the order they're kept here by python for proper
    # attribute calculation process
    preAssignment = 1
    preMul = 2
    preDiv = 3
    modAdd = 4
    modSub = 5
    postMul = 6
    postDiv = 7
    postPercent = 8
    postAssignment = 9
    # Following operators are for immediate modification
    increment = 10
    decrement = 11
    assignment = 12

    @classmethod
    def expressionValueToOperator(cls, expressionValue):
        """
        Convert expression value to operator.

        Positional arguments:
        expressionValue -- value of expression, which is supposed
        to be textual operator identifier

        Return value:
        ID of operator, corresponding to passed textual operator
        specifier, or None if no corresponding operator was found
        """
        # Format: {operator name: operator ID}
        conversionMap = {"PreAssignment": cls.preAssignment,
                         "PreMul": cls.preMul,
                         "PreDiv": cls.preDiv,
                         "ModAdd": cls.modAdd,
                         "ModSub": cls.modSub,
                         "PostMul": cls.postMul,
                         "PostDiv": cls.postDiv,
                         "PostPercent": cls.postPercent,
                         "PostAssignment": cls.postAssignment}
        try:
            result = conversionMap[expressionValue]
        except KeyError:
            result = None
        return result


class InfoSourceType:
    """Info source value type ID holder"""
    attribute = 1  # Source value is reference to attribute via ID, whose value should be used for modification
    value = 2  # Source value is actual value for modification


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
        # Boolean flag, identifying local/gang change.
        self.context = None
        # Time context in which modification is applied, must
        # be InfoRunTime class' attribute value.
        self.runTime = None
        # Target location to change, must be InfoLocation class'
        # attribute value.
        self.location = None
        # Filter type of the modification, must be None or
        # InfoFilterType class' attribute value.
        self.filterType = None
        # Filter value of the modification:
        # For filterType.all or filterType.None must be None;
        # For filterType.group must be some integer, referring group via ID;
        # For filterType.skill must be some integer, referring type via ID,
        # or const.Type.self_ to reference type of info carrier.
        self.filterValue = None
        # Which operation should be applied during modification,
        # must be InfoOperator class' attribute value.
        self.operator = None
        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.targetAttributeId = None
        # SourceValue type, must be InfoSourceType class'
        # attribute value.
        self.sourceType = None
        # Value which is used as modification value for operation:
        # For sourceType.attribute must be integer which refers attribute via ID;
        # For sourceType.value must be any value CCP can define in expression, integer or value.
        self.sourceValue = None
