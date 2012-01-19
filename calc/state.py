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


from eos.calc.info.info import InfoContext


class State:
    """
    Holds IDs of states all holders can take, and serves as glue between
    info contexts and holder states.
    """
    offline = 1
    online = 2
    active = 3
    overload = 4

    @classmethod
    def _context2state(cls, context):
        """
        Convert info context into state.

        Positional arguments:
        context -- ID of context to convert

        Return value:
        ID of state, corresponding to passed context, or None if
        no corresponding context was found
        """
        conversionMap = {InfoContext.passive: cls.offline,
                         InfoContext.online: cls.online,
                         InfoContext.active: cls.active,
                         InfoContext.overload: cls.overload}
        try:
            result = conversionMap[context]
        except KeyError:
            result = None
        return result

    @classmethod
    def _contextDifference(cls, state1, state2):
        """
        Get context difference between two states.

        Positional arguments:
        state1 -- ID of first state to compare, can be None
        state2 -- ID of second state to compare, can be None

        Return value:
        Set with context IDs, which need to be enabled/disabled to perform
        state switch
        """
        # If both passed state are the same, then
        # active contexts shouldn't differ too
        if state1 == state2:
            return set()
        # Dictionary which deals with conversion of state to context
        conversionMap = {cls.offline: InfoContext.passive,
                         cls.online: InfoContext.online,
                         cls.active: InfoContext.active,
                         cls.overload: InfoContext.overload}
        # Container which keeps all state IDs
        allStates = {cls.offline, cls.online,
                     cls.active, cls.overload}
        # To get active contexts for each state, we need to find which other states
        # passed state includes (all states  with equal or lower IDs), then transform
        # states we've got into context IDs
        contexts1 = set(conversionMap[state] for state in filter(lambda state: state <= state1, allStates)) if state1 is not None else None
        contexts2 = set(conversionMap[state] for state in filter(lambda state: state <= state2, allStates)) if state2 is not None else None
        # If one of passed states was None (if both were none, empty set should've been
        # returned already), return all contexts belonging to other state
        if contexts1 is None or contexts2 is None:
            result = contexts1 or contexts2
        # If both states were not None, get all contexts which are present
        # in one set but not in another
        else:
            result = contexts1.symmetric_difference(contexts2)
        return result
