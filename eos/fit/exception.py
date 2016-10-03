# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from eos.exception import EosError


class HolderAddError(EosError):
    """
    Base class for exceptions which occur during
    adding holder to fit.
    """
    pass


class HolderAlreadyAssignedError(HolderAddError):
    """
    Raised on attempt to add holder to fit, when
    it's already assigned.
    """
    pass


class HolderRemoveError(EosError):
    """
    Base class for exceptions which occur during
    holder removal from fit.
    """
    pass


class HolderFitMismatchError(HolderRemoveError):
    """
    Raised during removal of holder from fit,
    when holder's fit reference does not reference
    fit holder being removed from.
    """
    pass
