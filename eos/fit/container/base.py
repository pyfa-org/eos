# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from .exception import ItemAlreadyAssignedError


class ItemContainerBase:
    """Base class for item containers."""

    def __init__(self, item_class):
        """Initialize common container functionality.

        Args:
            item_class: Class of items this container is allowed to contain.
        """
        self.__item_class = item_class

    def _handle_item_addition(self, item, container):
        """Do all the generic work to add item to container.

        Must be called after item has been assigned to specific container, so
        that presence checks during addition pass.
        """
        # Make sure we're not adding item which already belongs to other
        # container
        if item._container:
            raise ItemAlreadyAssignedError(item)
        item._container = container

    def _handle_item_removal(self, item):
        """Do all the generic work to remove item to container.

        Must be called before item has been removed from specific container, so
        that presence checks during removal should pass.
        """
        item._container = None

    def _check_class(self, item, allow_none=False):
        """Check if class of passed item corresponds to our expectations.

        Args:
            item: Item which should be checked.
            allow_none (optional): Define if None as item is fine or not. By
                default, it is not.

        Raises:
            TypeError: If item class check fails.
        """
        if isinstance(item, self.__item_class):
            return
        if item is None and allow_none is True:
            return
        msg = 'only {} {} accepted, not {}'.format(
            self.__item_class,
            'or None are' if allow_none is True else 'is',
            type(item)
        )
        raise TypeError(msg)
