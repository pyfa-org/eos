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


class HolderContainerBase:
    """
    Base class for any containers which are intended
    to ease management of holders. Hides fit-specific
    logic under its hood, letting real containers (which
    should inherit it) implement just container type-
    specific logic.

    Positional arguments:
    fit -- fit, to which container is attached
    holder_class -- class of holders this container
    is allowed to contain
    """

    __slots__ = ('__fit', '__holder_class')

    def __init__(self, fit, holder_class):
        self.__fit = fit
        self.__holder_class = holder_class

    def _check_class(self, holder, allow_none=False):
        """
        Check if class of passed holder corresponds
        to our expectations.
        """
        if isinstance(holder, self.__holder_class):
            return
        if holder is None and allow_none is True:
            return
        msg = 'only {} {} accepted, not {}'.format(
            self.__holder_class,
            'or None are' if allow_none is True else 'is',
            type(holder)
        )
        raise TypeError(msg)

    def _handle_add(self, holder):
        """Shortcut for registration of holder in fit."""
        self.__fit._add_holder(holder)

    def _handle_remove(self, holder):
        """Shortcut for unregistration of holder in fit."""
        self.__fit._remove_holder(holder)
