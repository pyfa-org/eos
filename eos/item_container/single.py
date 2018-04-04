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


from .base import ItemContainerBase
from .exception import ItemAlreadyAssignedError


class ItemDescriptor(ItemContainerBase):
    """Container for single item.

    Args:
        attr_name: Name of instance attribute which should be used to store data
            processed by the descriptor.
        item_class: Class of items this container is allowed to contain.
    """

    def __init__(self, attr_name, item_class):
        ItemContainerBase.__init__(self, item_class)
        self.__attr_name = self.__mangle_attr_name(attr_name)

    def __get__(self, instance, parent):
        if instance is None:
            return self
        return getattr(instance, self.__attr_name, None)

    def __set__(self, instance, new_item):
        self._check_class(new_item, allow_none=True)
        attr_name = self.__attr_name
        old_item = getattr(instance, attr_name, None)
        if old_item is not None:
            self._handle_item_removal(old_item)
        setattr(instance, attr_name, new_item)
        if new_item is not None:
            try:
                self._handle_item_addition(new_item, instance)
            except ItemAlreadyAssignedError as e:
                setattr(instance, attr_name, old_item)
                if old_item is not None:
                    self._handle_item_addition(old_item, instance)
                raise ValueError(*e.args) from e

    def __mangle_attr_name(self, attr_name):
        if attr_name.startswith('__') and not attr_name.endswith('__'):
            return '_{}{}'.format(type(self).__name__, attr_name)
        return attr_name
