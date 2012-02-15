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


from eos.const import State, Location, Context, RunTime, SourceType
from .affector import Affector
from .register import LinkRegister


class LinkTracker:
    """
    Serve as intermediate layer between fit and holder link register.
    Implements methods which make it easier for fit to add, modify and
    remove holders, and exposes two main register getters for external
    use.

    Positional arguments:
    fit -- Fit object to which tracker is assigned
    """

    def __init__(self, fit):
        self.__fit = fit
        self.__register = LinkRegister(fit)
        self.__holderStates = {}

    def getAffectors(self, holder, attrId=None):
        """
        Get affectors, influencing passed holder.

        Positional arguments:
        holder -- holder, for which we're getting affectors

        Keyword arguments:
        attrId -- target attribute ID filters; only affectors
        which influence attribute with this ID will be returned.
        If None, all affectors influencing holder are returned
        (default None)

        Return value:
        Set with Affector objects
        """
        if attrId is None:
            affectors = self.__register.getAffectors(holder)
        else:
            affectors = set()
            for affector in self.__register.getAffectors(holder):
                if affector.info.targetAttributeId == attrId:
                    affectors.add(affector)
        return affectors

    def getAffectees(self, affector):
        """
        Get affectees being influenced by affector.

        Positional arguments:
        affector -- affector, for which we're getting affectees

        Return value:
        Set with holders
        """
        return self.__register.getAffectees(affector)

    def __getHolderDirectLocation(self, holder):
        """
        Get location which you need to target to apply
        direct holder modification.

        Positional arguments:
        holder -- holder in question

        Return value:
        Location specification, if holder can be targeted directly
        from the outside, or None if it can't
        """
        # For ship and character it's easy, we're just picking
        # corresponding location
        if holder is self.__fit.ship:
            location = Location.ship
        elif holder is self.__fit.character:
            location = Location.character
        # For "other" location, we should've checked for presence
        # of other entity - charge's container or module's charge
        elif getattr(holder, "_other", None) is not None:
            location = Location.other
        else:
            location = None
        return location

    def addHolder(self, holder):
        """
        Track links between passed holder and already
        tracked holders.

        Positional arguments:
        holder -- holder which is added to tracker
        """
        enabledDirectLocation = self.__getHolderDirectLocation(holder)
        self.__register.registerAffectee(holder, enableDirect=enabledDirectLocation)

    def removeHolder(self, holder):
        """
        Stop tracking links between passed holder
        and remaining tracked holders.

        Positional arguments:
        holder -- holder which is removed from tracker
        """
        disabledDirectLocation = self.__getHolderDirectLocation(holder)
        self.__register.unregisterAffectee(holder, disableDirect=disabledDirectLocation)

    def stateSwitch(self, holder, oldState, newState):
        """
        Handle holder state switch in link tracker. Toggles holder's
        effects on another holders.

        Positional arguments:
        holder -- holder which has its state changed
        oldState -- state from which holder is being switched
        newState -- state to which holder is being switched
        """
        # Get set of affectors which we will need to register or
        # unregister
        stateDifference = self.__stateDifference(oldState, newState)
        processedContexts = {Context.local}
        affectorDiff = self.__generateDurationAffectors(holder, stateFilter=stateDifference, contextFilter=processedContexts)
        # Register them, if we're turning something on
        if oldState is None or (newState is not None and newState > oldState):
            for affector in affectorDiff:
                self.__register.registerAffector(affector)
            self.__clearAffectorsDependents(affectorDiff)
        # Unregister, if we're turning something off
        else:
            self.__clearAffectorsDependents(affectorDiff)
            for affector in affectorDiff:
                self.__register.unregisterAffector(affector)

    def __stateDifference(self, state1, state2):
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
        # If both passed states are the same, no state
        # switch needed
        if state1 == state2:
            return set()
        # Container which keeps all state IDs
        allStates = {State.offline, State.online,
                     State.active, State.overload}
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

    def clearHolderAttributeDependents(self, holder, attrId):
        """
        Clear calculated attributes relying on passed attribute.

        Positional arguments:
        holder -- holder, which carries attribute in question
        attrId -- ID of attribute
        """
        for affector in self.__generateDurationAffectors(holder):
            info = affector.info
            # Skip affectors which do not use attribute being damaged as source
            if info.sourceValue != attrId or info.sourceType != SourceType.attribute:
                continue
            # Go through all holders targeted by info
            for targetHolder in self.getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[info.targetAttributeId]

    def __clearAffectorsDependents(self, affectors):
        """
        Clear calculated attributes relying on affectors.

        Positional arguments:
        affectors -- iterable with affectors in question
        """
        for affector in affectors:
            # Go through all holders targeted by info
            for targetHolder in self.getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[affector.info.targetAttributeId]

    def __generateDurationAffectors(self, holder, stateFilter=None, contextFilter=None):
        """
        Get all duration affectors spawned by holder.

        Positional arguments:
        holder -- holder, for which affectors are generated

        Keyword arguments:
        stateFilter -- filter results by affector's required state,
        which should be in this iterable; if None, no filtering
        occurs (default None)
        contextFilter -- filter results by affector's required state,
        which should be in this iterable; if None, no filtering
        occurs (default None)

        Return value:
        Set with Affector objects, satisfying passed filters
        """
        affectors = set()
        for info in holder.item.getInfos(self.__fit._eos._logger):
            if stateFilter is not None and not info.state in stateFilter:
                continue
            if contextFilter is not None and not info.context in contextFilter:
                continue
            if info.runTime != RunTime.duration:
                continue
            affector = Affector(holder, info)
            affectors.add(affector)
        return affectors
