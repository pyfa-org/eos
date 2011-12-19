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

class ConditionEval:
    """
    This class is used to evaluate the conditions on an info object and see if they are met
    """
    def __init__(self, holder, info):
        self.info = info
        """The info object to evaluate for"""


    def __call__(self, holder):
        """
        __call__ method, makes objects of this class directly callable.
        They take 1 argument: the holder against which to evaluate the condition
        """
        if self.info.conditions is None:
            return True
        else:
            return True