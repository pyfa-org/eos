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


class State:
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
