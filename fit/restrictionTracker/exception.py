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


from eos.exception import EosException


class RestrictionTrackerException(EosException):
    """All restriction tracker exceptions are based on this class."""
    pass


class CpuException(RestrictionTrackerException):
    """Raised when ship doesn't have enough cpus to fit all modules."""
    pass


class HighSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough high slots to fit all modules."""
    pass


class MaxGroupFittedException(RestrictionTrackerException):
    """Raised when excessive modules of certain group are fitted to ship."""
    pass


class ShipGroupException(RestrictionTrackerException):
    """Raised when item cannot be fitted to ship of given group."""
    pass

class CapitalModuleException(RestrictionTrackerException):
    """Raised when capital modules are fit on non-capital ship."""
    pass
