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


from eos.fit.message.helper import MsgHelper
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
        item._container = container
        fit = item._fit
        if fit is not None:
            for subitem in self.__subitem_iter(item):
                msgs = MsgHelper.get_item_added_msgs(subitem)
                fit._publish_bulk(msgs)
                subitem._load()

    def _handle_item_removal(self, item):
        """Do all the generic work to remove item to container.

        Must be called before item has been removed from specific container, so
        that presence checks during removal pass.
        """
        fit = item._fit
        for subitem in self.__subitem_iter(item):
            subitem._unload()
            if fit is not None:
                msgs = MsgHelper.get_item_removed_msgs(subitem)
                fit._publish_bulk(msgs)
        item._container = None

    def __subitem_iter(self, item):
        """Iterate through passed item and its child items."""
        yield item
        # Skip autoloaded items because they are handled by loading or unloading
        # of parent item
        for child_item in item._child_item_iter(skip_autoitems=True):
            yield child_item

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
