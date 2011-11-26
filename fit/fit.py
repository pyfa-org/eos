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

import collections
import itertools

class Fit(object):
    '''
    Fit object. Each fit is built out of a number of Modules, as well as a Ship.
    This class also contains the logic to apply a single expressionInfo onto itself
    '''

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, ship):
        self._unsetHolder(self.__ship)
        self.__ship = ship
        self._setHolder(ship)

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, character):
        self._unsetHolder(self.__character)
        self.__character = character
        self._setHolder(character)

    def __init__(self, ship):
        '''
        Constructor: Accepts a Ship
        '''
        # These registers are mainly used when new modules are added.
        # A new module addition will cause registers to be checked for all that module's skills and group for effects to apply to it
        # They usualy should NOT be changed outside the lib
        self.__skillAffectorRegister = {}
        self.__groupAffectorRegister = {}

        self.__groupAffecteeRegister = {}
        self.__skillAffecteeRegister = {}

        # Vars used by properties
        self.__ship = None
        self.__character = None

        # Public stuff
        self.modules = MutableAttributeHolderList(self)
        self.ship = ship

        self.__holderAttributeOperationsRegister = {}

    def calculate(self):
        """
        Calculate all attributes on the fit.
        This method will ONLY calculate whats needed
        """

    def _registerHolder(self, holder):
        skillAffecteeRegister = self.__skillAffecteeRegister
        for req in holder.type.requiredSkills():
            l = skillAffecteeRegister.get(req)
            if l is None:
                l = skillAffecteeRegister[req] = set()

            l.add(holder)

        groupId = holder.type.groupId
        l = self.__groupAffecteeRegister.get(groupId)
        if l is None:
            l = self.__groupAffecteeRegister[groupId] = set()

        l.add(holder)

    def _unregisterHolder(self, holder):
        skillAffecteeRegister = self.__skillAffecteeRegister
        for req in holder.type.requiredSkills():
            skillAffecteeRegister[req].remove(holder)

        self.__groupAffecteeRegister[holder.type.groupId].remove(holder)

    def _prepare(self, holder, info):
        '''
        Prepare the passed info object for execution
        '''
        # Fill up the registers
        skillAffectorRegister = self.__skillAffectorRegister
        groupAffectorRegister = self.__groupAffectorRegister

        for filter in info.filters:
            if filter.type == "skill":
                #Get the affector set
                s = skillAffectorRegister.get(filter.value)
                if s is None:
                    skillAffectorRegister[filter.value] = s = set()

                s.add(holder)

            elif filter.type == "group":
                s = groupAffectorRegister.get(filter.value)
                if s is None:
                    groupAffectorRegister[filter.value] = s = set()

                s.add(holder)

        for target in self.__getTargets(holder, info):
            target._register(holder, info)

        # Cast out damage on the freshly prepared info to reset any calculated values that it might affect
        self._damage(holder, info)

    def _damage(self, sourceHolder, info):
        """
        - Lookup all the targets of the passed info object on the passed holder
        - For each of the found targets: damage the attribute that will be affected
        """
        for target in self.__getTargets(sourceHolder, info):
            target._damage(info)

    def _undo(self, holder, info):
        '''
        Undos the operations applied by _run, usualy also called by the ExpressionEval that owns this ExpressionInfo.
        Unless you're running custom ExpressionInfo objects, you will usualy never call this
        '''
        pass

    def __getTargets(self, holder, info):
        '''
        Returns the target(s) of the passed expression.
        Implemented values: Self, Ship, Char
        Unimplemented values: Target, Area, Other
        '''
        target = info.target

        if target == "Self":
            return (holder, )
        #Ship can either mean the ship itself (if no filters are specified)
        #or a filtered match on everything on the fit (if filters are specified)
        elif target == "Ship" and len(info.filters) > 0:
            filters = info.filters
            return [mod for mod in self.modules if mod.matches(filters)]
        elif target == "Ship":
            return (self.ship, )
        elif target == "Char":
            return (self.character, )

    def __setFit(self, holder):
        if(holder != None):
            holder.fit = self

    def _setHolder(self, holder):
        if holder is not None:
            # Make sure the module isn't used elsewhere already
            if holder.fit is not None:
                raise ValueError("Cannot add a module which is already in another fit")

            holder.fit = self
            self._registerHolder(holder)
            holder._prepare()

    def _unsetHolder(self, holder):
        if holder is not None:
            assert(holder.fit == self)
            self._unregisterHolder(holder)
            holder.fit = None

class MutableAttributeHolderList(collections.MutableSequence):
    '''
    Class implementing the MutableSequence ABC intended to hold a list of MutableAttributeHolders (typically: modules, drones, etc.).
    It makes sure the module knows its been added onto the fit, and makes sure a module is only in one single fit
    '''
    def __init__(self, fit):
        self.__fit = fit
        self.__list = [] # List used for storage internally

    def __setitem__(self, index, holder):
        existing = self.__list.get(index)
        if(existing != None):
            self.fit._unsetHolder(existing)

        self.__list.__setitem__(index, holder)
        self.__fit._setHolder(holder)

    def __delitem__(self, index):
        self.__fit._unsetHolder(self.__list[index])
        return self.__list.__delitem__(index)

    def __getitem__(self, index):
        return self.__list.__getitem__(index)

    def __len__(self):
        return self.__list.__len__()

    def insert(self, index, holder):
        self.__list.insert(index, holder)
        self.__fit._setHolder(holder)