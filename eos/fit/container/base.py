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


from eos.fit.message.helper import (
    get_items_added_messages, get_items_removed_messages)
from .exception import ItemAlreadyAssignedError


class ItemContainerBase:
    """Base class for item containers.

    Args:
        item_class: Class of items this container is allowed to contain.
    """

    def __init__(self, item_class):
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
        # Item updates
        item._container = container
        child_items = item._child_items
        for subitem in (item, *child_items):
            subitem._refresh_source()
        # Fit updates
        fit = item._fit
        if fit is not None:
            # Notify services about added item
            if fit.source is not None:
                fit._publish_bulk(
                    get_items_added_messages((item, *child_items)))
            # Volatile cache
            for subitem in (item, *child_items):
                fit._volatile_mgr.add_volatile_object(subitem)
            fit._volatile_mgr.clear_volatile_attrs()

    def _handle_item_removal(self, item):
        """Do all the generic work to remove item to container.

        Must be called before item has been removed from specific container, so
        that presence checks during removal should pass.
        """
        # Fit updates
        child_items = item._child_items
        fit = item._fit
        if fit is not None:
            # Notify services about removed item
            if fit.source is not None:
                fit._publish_bulk(
                    get_items_removed_messages((*child_items, item)))
            # Volatile cache
            fit._volatile_mgr.clear_volatile_attrs()
            for subitem in (*child_items, item):
                fit._volatile_mgr.remove_volatile_object(subitem)
        # Item updates
        item._container = None
        for subitem in (item, *child_items):
            subitem._refresh_source()

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
            self.__item_class, 'or None are' if allow_none is True else 'is',
            type(item))
        raise TypeError(msg)
