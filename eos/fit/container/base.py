# ===============================================================================
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
# ===============================================================================


from .exception import ItemAlreadyAssignedError, ItemFitMismatchError
from eos.fit.messages import ItemAdded, ItemRemoved


class ItemContainerBase:
    """
    Base class for any containers which are intended
    to ease management of items. Hides fit-specific
    logic under its hood, letting real containers (which
    should inherit it) implement just container type-
    specific logic.

    Required arguments:
    fit -- fit, to which container is attached
    item_class -- class of items this container
        is allowed to contain
    """

    def __init__(self, item_class):
        self.__item_class = item_class

    def _handle_item_addition(self, fit, item):
        """
        Do all the generic work to add item to container.
        Must be called after item has been assigned to
        specific container.
        """
        # Make sure we're not adding item which already
        # belongs to other fit
        if item._fit is not None:
            raise ItemAlreadyAssignedError(item)
        # Finalize linking items before handling sub-items
        # and firing an event. This way we ensure that all
        # services  which may rely on fit/item links will
        # work properly
        item._fit = fit
        # Do not check if charge has proper fit link, because
        # consistency is kept by charge descriptor. We should
        # never get an exception here
        charge = getattr(item, 'charge', None)
        if charge is not None:
            self._handle_item_addition(fit, charge)
        fit._publish(ItemAdded(item))

    def _handle_item_removal(self, fit, item):
        """
        Do all the generic work to remove item to container.
        Must be called before item has been removed from
        specific container.
        """
        # If everything is alright, this should never
        # be raised regardless of user actions
        if item._fit is not fit:
            raise ItemFitMismatchError(item)
        # Fire removal event before unlinking, same reason
        # as in addition handling method
        fit._publish(ItemRemoved(item))
        charge = getattr(item, 'charge', None)
        if charge is not None:
            self._handle_item_removal(fit, charge)
        item._fit = None

    def _check_class(self, item, allow_none=False):
        """
        Check if class of passed item corresponds
        to our expectations.
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
