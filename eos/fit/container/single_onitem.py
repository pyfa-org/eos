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


from .base import ItemContainerBase


class ItemDescriptorOnItem(ItemContainerBase):
    """
    Container for single item, intended to be used
    as item attribute for direct access.

    Required arguments:
    direct_attr_name -- name of instance attribute which
        should be used to store data processed by descriptor
    reverse_attr_name -- name of attribute which will be
        used to refer from contained item to container
        item, can be None (no reference to container)
    item_class -- class of items this container
        is allowed to contain
    """

    def __init__(self, direct_attr_name, reverse_attr_name, item_class):
        ItemContainerBase.__init__(self, item_class)
        self.__direct_attr_name = direct_attr_name
        self.__reverse_attr_name = reverse_attr_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.__direct_attr_name, None)

    def __set__(self, instance, new_item):
        self._check_class(new_item, allow_none=True)
        # Check if passed item is attached to other fit already
        # or not. We can't rely on fit._add_item to do it,
        # because charge can be assigned when container is detached
        # from fit, which breaks consistency - both items
        # need to be assigned to the same fit
        if new_item is not None and new_item._fit is not None:
            raise ValueError(new_item)
        fit = instance._fit
        direct_attr_name = self.__direct_attr_name
        reverse_attr_name = self.__reverse_attr_name
        old_item = getattr(instance, direct_attr_name, None)
        if old_item is not None:
            if fit is not None:
                self._handle_item_removal(fit, old_item)
            if reverse_attr_name is not None:
                setattr(old_item, reverse_attr_name, None)
        setattr(instance, direct_attr_name, new_item)
        if new_item is not None:
            if reverse_attr_name is not None:
                setattr(new_item, reverse_attr_name, instance)
            if fit is not None:
                self._handle_item_addition(fit, new_item)
