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


"""
Module with functions intended to be used as holder
subclass methods. They are stored here only when more
than 1, but not all holder types are using it.
"""

# Used by Module, Drone
def setState(holder, newState):
    if newState == holder.state:
        return
    # When holder is assigned to some fit, ask fit to perform
    # fit-specific state switch of our holder
    if holder._fit is not None:
        holder._fit._holderStateSwitch(holder, newState)
    holder._state = newState
