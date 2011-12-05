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

from eos import const
from abc import ABCMeta
from abc import abstractproperty

RegistrationInfo = collections.namedtuple("RegistrationInfo", ("sourceHolder", "info"))

class MutableAttributeHolder(object):
    """
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def location(self):
        ...

    def __init__(self, type):
        """
        Constructor. Accepts a Type
        """
        self.fit = None
        """
        Which fit this holder is bound to
        """
        self.type = type
        """
        Which type this holder wraps
        """

        self.attributes = MutableAttributeMap(self)
        """
        Special dictionary subclass that holds modified attributes and data related to their calculation
        """

    def _register(self):
        self.attributes._register()

    def _unregister(self):
        self.attributes._unregister()

class MutableAttributeMap(collections.Mapping):
    """
    MutableAttributeMap class, this class is what actually keeps track of modified attribute values and who modified what so undo can work as expected.
    """

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

    def _register(self):
        pass

    def _unregister(self):
        pass

    def __calculate(self, attrId):
        """
        Run calculations to find the actual value of attribute with ID equal to attrID.
        All other attribute values are assumed to be final.
        This is obviously not always the case,
        if any of the dependencies of this calculation change, this attribute will get damaged and thus recalculated
        """

        base = self.__holder.type.attributes.get(attrId)
        modifiers = {}

        try:
            register = self.__attributeRegister[attrId]
            result = base
            for sourceHolder, info in register:
                modValue = sourceHolder.attributes[info.sourceAttributeId]
                operation = info.operation
                if not operation in modifiers:
                    modifiers[operation] = []
                modifiers[operation].append(modValue)

            for operation in sorted(modifiers):
                if operation in (const.optrPreAssignment, const.optrPostAssignment):
                    for mod in modifiers[operation]:
                        result = mod
                elif operation in (const.optrPreMul, const.optrPostMul):
                    for mod in modifiers[operation]:
                        result *= mod
                elif operation == const.optrPostPercent:
                    for mod in modifiers[operation]:
                        result *= 1 + mod / 100
                elif operation in (const.optrPreDiv, const.optrPostDiv):
                    for mod in modifiers[operation]:
                        result /= mod
                elif operation == const.optrModAdd:
                    for mod in modifiers[operation]:
                        result += mod
                elif operation == const.optrModSub:
                    for mod in modifiers[operation]:
                        result -= mod

            return result
        except:
            return base
