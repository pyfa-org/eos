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

RegistrationInfo = collections.namedtuple("RegistrationInfo", ("sourceHolder", "info"))

class MutableAttributeHolder(object):
    '''
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    '''

    def __init__(self, type):
        '''
        Constructor. Accepts a Type
        '''
        self.fit = None
        '''
        Which fit this holder is bound to
        '''
        self.type = type
        '''
        Which type this holder wraps
        '''

        self.attributes = MutableAttributeMap(self)
        '''
        Special dictionary subclass that holds modified attributes and data related to their calculation
        '''

    def _prepare(self):
        for effect in self.type.effects:
            effect._prepare(self, self.fit)

    def _apply(self):
        """
        Applies all effects of the type bound to this holder. This can have for reaching consequences as it can affect anything fitted onto the fit (including itself)
        This is typically automatically called by eos when relevant (when a holder is added onto a fit)
        """
        for effect in self.type.effects:
            effect._apply(self, self.fit)


    def _undo(self):
        """
        Undos the operations done by apply
        This is typically automatically called by eos when relevant (when a holder is removed from a fit)
        """
        for effect in self.type.effects:
            effect._undo(self.fit)

    def matches(self, filters):
        """
        Checks whether this holder matches the passed filter definitions
        """
        type = self.type
        for filter in filters:
            if filter.type == "group" and filter.value != type.groupId:
                return False
            if filter.type == "skill" and filter.value not in type.requiredSkills():
                return False

        return True

    def _register(self, sourceHolder, info):
        self.attributes._register(sourceHolder, info)

    def _damage(self, info):
        self.attributes._damage(info)

class MutableAttributeMap(collections.Mapping):
    '''
    MutableAttributeMap class, this class is what actually keeps track of modified attribute values and who modified what so undo can work as expected.
    '''
    order = {"PreAssignment": 1,
         "PreMul": 2,
         "PreDiv": 3,
         "ModAdd": 4,
         "ModSub": 5,
         "PostMul": 6,
         "PostDiv": 7,
         "PostPercent": 8,
         "PostAssignment": 9}

    def __init__(self, holder):
        self.__holder = holder
        self.__modifiedAttributes = {}

        # The attribute register keeps track of what effects apply to what attribute
        self.__attributeRegister = {}

    def __getitem__(self, key):
        val = self.__modifiedAttributes.get(key)
        if val is None:
            # Should actually run calcs here instead :D
            self.__modifiedAttributes[key] = val = self.__calculate(key)

        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.__modifiedAttributes or key in self.__holder.type.attributes

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        return set(self.__modifiedAttributes.keys()).intersection(self.__holder.type.attributes.keys())

    def _register(self, sourceHolder, info):
        """
        Register an info object for processing
        """
        register = self.__attributeRegister.get(info.targetAttributeId)
        if register is None:
            register = self.__attributeRegister[info.targetAttributeId] = set()

        registrationInfo = RegistrationInfo(sourceHolder, info)
        register.add(registrationInfo)
        return registrationInfo

    def _damage(self, info):
        """
        Cause damage on self using a certain info object.
        This is a recursive method that does the following:
        - Clear the calculated values for the target of the passed info object
        - For each info using the cleared value as source, call fit.damage
        """

        holder = self.__holder
        fit = holder.fit
        targetAttributeId = info.targetAttributeId

        try:
            del self.__modifiedAttributes[targetAttributeId]
        except KeyError:
            pass
        finally:
            for attrId, s in self.__attributeRegister.items():
                for registrationInfo in s:
                    newInfo = registrationInfo.info
                    if newInfo.sourceAttributeId == targetAttributeId:
                        fit.damage(self, newInfo)



    def __calculate(self, key):
        """
        Run calculations to find the actual value of key.
        All other attribute values are assumed to be final.
        This is obviously not always the case,
        if any of the dependencies of this calculation change, this attrib will get damaged and thus recalculated
        """

        base = self.__holder.type.attributes.get(key)

        try:
            order = self.order
            register = sorted(self.__attributeRegister[key], key=lambda k: order[k.info.operation])

            result = base
            for sourceHolder, info in register:
                value = sourceHolder.attributes[info.sourceAttributeId]
                operation = info.operation

                if operation in ("PreAssignment", "PostAssignment"):
                    result = value
                elif operation in ("PreMul", "PostMul"):
                    result *= value
                elif operation == "PostPercent":
                    result *= 1 + value / 100
                elif operation in ("PreDiv", "PostDiv"):
                    result /= value
                elif operation == "ModAdd":
                    result += value
                elif operation == "ModSub":
                    result -= value

                return result
        except:
            return base
