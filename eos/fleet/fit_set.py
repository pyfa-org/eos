# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from eos.pubsub.message import FleetFitAdded
from eos.pubsub.message import FleetFitRemoved


class FitSet:
    """Unordered container for fits.

    Implements set-like interface.

    Args:
        fleet: Fleet this container is attached to.
    """

    def __init__(self, fleet):
        self.__fleet = fleet
        self.__set = set()

    # Modifying methods
    def add(self, fit):
        """Add fit to the container.

        Args:
            fit: Fit to add.

        Raises:
            ValueError: If fit cannot be added to the container (e.g. already
                belongs to some fleet).
        """
        if fit._fleet is not None:
            raise ValueError(fit)
        self.__set.add(fit)
        fit._fleet = self.__fleet
        fit._publish(FleetFitAdded())

    def remove(self, fit):
        """Remove fit from the container.

        Args:
            fit: Fit to remove.

        Raises:
            KeyError: If fit cannot be removed from the container (e.g. it
                doesn't belong to it).
        """
        if fit not in self.__set:
            raise KeyError(fit)
        self.__handle_fit_removal(fit)

    def clear(self):
        """Remove everything from the container."""
        for fit in set(self.__set):
            self.__handle_fit_removal(fit)

    def __handle_fit_removal(self, fit):
        fit._publish(FleetFitRemoved())
        self.__set.remove(fit)
        fit._fleet = None

    # Non-modifying methods
    def __iter__(self):
        return iter(self.__set)

    def __contains__(self, fit):
        return fit in self.__set

    def __len__(self):
        return len(self.__set)

    # Auxiliary methods
    def __repr__(self):
        return repr(self.__set)
