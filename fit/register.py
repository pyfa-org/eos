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

class Register():
    """
    Register class. Keeps track of fit specific
    """
    def __init__(self, fit):
        self.__fit = fit
        """The fit we're keeping track of things for"""

        self.__affectorSpecificLocation = {}
        """
        Stores all (sourceHolder, info) tuples that directly affect a certain location.
        Key: locationId
        Value: set of (sourceHolder, info) tuples
        """

        self.__affectorAllLocation = {}
        """
        Stores all (sourceHolder, info) tuples that affect all holders in a certain location
        Key: locationId
        Value: set of (sourceHolder, info) tuples
        """


        self.__affectorGroupLocation = {}
        """
        Stores all (sourceHolder, info) tuples that affect everything in a certain location using a certain group-based filter
        Key: locationId
        Value: dictionary
            Key: groupId
            Value: set of (sourceHolder, info) tuples
        """

        self.__affectorSkillLocation = {}
        """
        Stores all (sourceHolder, info) tuples that affect everything in a certain location using a certain skill-based filter
        Key: locationId
        Value: dictionary
            key: skillId
            Value: set of (sourceHolder, info) tuples
        """