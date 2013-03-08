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


from eos.const.eos import Context
from .affector import Affector
from .register import LinkRegister


class LinkTracker:
    """
    Serve as intermediate layer between fit and holder link register.
    Implements methods which make it easier for fit to add, modify and
    remove holders (by implementing higher-level logic which deals with
    state, context and attribute filters), and exposes two main register
    getters for external use.

    Positional arguments:
    fit -- Fit object to which tracker is assigned
    """

    def __init__(self, fit):
        self._fit = fit
        self._register = LinkRegister(fit)

    def getAffectors(self, holder, attrId=None):
        """
        Get affectors, influencing passed holder.

        Positional arguments:
        holder -- holder, for which we're getting affectors

        Keyword arguments:
        attrId -- target attribute ID filter; only affectors
        which influence attribute with this ID will be returned.
        If None, all affectors influencing holder are returned
        (default None)

        Return value:
        Set with Affector objects
        """
        if attrId is None:
            affectors = self._register.getAffectors(holder)
        else:
            affectors = set()
            for affector in self._register.getAffectors(holder):
                if affector.modifier.targetAttributeId == attrId:
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
        return self._register.getAffectees(affector)

    def addHolder(self, holder):
        """
        Track links between passed holder and already
        tracked holders.

        Positional arguments:
        holder -- holder which is added to tracker
        """
        self._register.registerAffectee(holder)

    def removeHolder(self, holder):
        """
        Stop tracking links between passed holder
        and remaining tracked holders.

        Positional arguments:
        holder -- holder which is removed from tracker
        """
        self._register.unregisterAffectee(holder)

    def enableStates(self, holder, states):
        """
        Handle state switch upwards.

        Positional arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for initial state
        """
        processedContexts = (Context.local,)
        enabledAffectors = self.__generateAffectors(holder, stateFilter=states, contextFilter=processedContexts)
        # Clear attributes only after registration jobs
        for affector in enabledAffectors:
            self._register.registerAffector(affector)
        self.__clearAffectorsDependents(enabledAffectors)

    def disableStates(self, holder, states):
        """
        Handle state switch downwards.

        Positional arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for final state
        """
        processedContexts = (Context.local,)
        disabledAffectors = self.__generateAffectors(holder, stateFilter=states, contextFilter=processedContexts)
        # Clear attributes before unregistering, otherwise
        # we won't clean them up properly
        self.__clearAffectorsDependents(disabledAffectors)
        for affector in disabledAffectors:
            self._register.unregisterAffector(affector)

    def clearHolderAttributeDependents(self, holder, attrId):
        """
        Clear calculated attributes relying on passed attribute.

        Positional arguments:
        holder -- holder, which carries attribute in question
        attrId -- ID of attribute
        """
        # Clear attributes capped by this attribute
        capMap = holder.attributes._capMap
        if capMap is not None:
            for cappedAttrId in (capMap.get(attrId) or ()):
                del holder.attributes[cappedAttrId]
        # Clear attributes using this attribute as data source
        for affector in self.__generateAffectors(holder):
            modifier = affector.modifier
            # Skip affectors which do not use attribute being damaged as source
            if modifier.sourceAttributeId != attrId:
                continue
            # Go through all holders targeted by modifier
            for targetHolder in self.getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[modifier.targetAttributeId]

    def __clearAffectorsDependents(self, affectors):
        """
        Clear calculated attributes relying on affectors.

        Positional arguments:
        affectors -- iterable with affectors in question
        """
        for affector in affectors:
            # Go through all holders targeted by modifier
            for targetHolder in self.getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[affector.modifier.targetAttributeId]

    def __generateAffectors(self, holder, stateFilter=None, contextFilter=None):
        """
        Get all affectors spawned by holder.

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
        for modifier in holder.item.modifiers:
            if stateFilter is not None and not modifier.state in stateFilter:
                continue
            if contextFilter is not None and not modifier.context in contextFilter:
                continue
            affector = Affector(holder, modifier)
            affectors.add(affector)
        return affectors
