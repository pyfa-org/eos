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


from abc import ABCMeta, abstractmethod


class StatRegister(metaclass=ABCMeta):
    """Base class for all statistics registers."""

    @abstractmethod
    def register_holder(self, holder):
        """
        Perform registration jobs upon holder. Only immutable
        holder properties should be used during process.

        Posiitional arguments:
        holder -- holder to register
        """
        ...

    @abstractmethod
    def unregister_holder(self, holder):
        """
        Perform unregistration jobs upon holder. Only immutable
        holder properties should be used during process.

        Posiitional arguments:
        holder -- holder to unregister
        """
        ...
