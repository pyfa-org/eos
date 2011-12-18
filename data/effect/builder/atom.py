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

class ConditionAtom(object):
    """
    Stores bit of Info condition metadata
    """
    def __init__(self):
        self.type = None
        """
        Describes purpose of this atom.
        Must take any atomType* value from consts.
        """

        self.operator = None
        """
        For some atom types, describes which operation should be applied onto its arguments.
        For atomTypeLogic, holds atomLogic* from const file.
        For atomTypeComp, holds atomComp* from const file.
        For atomTypeMath, holds atomMath* from const file.
        """

        self.arg1 = None
        """
        For all types besides atomTypeVal, contains reference to child atom.
        """

        self.arg2 = None
        """
        For all types besides atomTypeVal, contains reference to child atom.
        """

        self.value = None
        """
        For atomTypeVal, contains pre-stored atom value.
        """

        self.carrier = None
        """
        For atomTypeValRef, contains reference to some location.
        """

        self.attribute = None
        """
        For atomTypeValRef, contains reference to attribute in some location.
        """

    # TODO: add some self-validation method, like for modifier object
