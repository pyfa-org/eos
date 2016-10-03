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


from .base import HolderContainerBase


class HolderDescriptorOnHolder(HolderContainerBase):
    """
    Container for single holder, intended to be used
    as holder attribute for direct access.

    Required arguments:
    direct_attr_name -- name of instance attribute which
    should be used to store data processed by descriptor
    reverse_attr_name -- name of attribute which will be
    used to refer from contained holder to container holder,
    can be None (no reference to container)
    holder_class -- class of holders this container
    is allowed to contain
    """

    def __init__(self, direct_attr_name, reverse_attr_name, holder_class):
        HolderContainerBase.__init__(self, holder_class)
        self.__direct_attr_name = direct_attr_name
        self.__reverse_attr_name = reverse_attr_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.__direct_attr_name, None)

    def __set__(self, instance, new_holder):
        self._check_class(new_holder, allow_none=True)
        # Check if passed holder is attached to other fit already
        # or not. We can't rely on fit._add_holder to do it,
        # because charge can be assigned when container is detached
        # from fit, which breaks consistency - both holders
        # need to be assigned to the same fit
        if new_holder is not None and new_holder._fit is not None:
            raise ValueError(new_holder)
        fit = instance._fit
        direct_attr_name = self.__direct_attr_name
        reverse_attr_name = self.__reverse_attr_name
        old_holder = getattr(instance, direct_attr_name, None)
        if old_holder is not None:
            if fit is not None:
                fit._request_volatile_cleanup()
                fit._remove_holder(old_holder)
            if reverse_attr_name is not None:
                setattr(old_holder, reverse_attr_name, None)
        setattr(instance, direct_attr_name, new_holder)
        if new_holder is not None:
            if reverse_attr_name is not None:
                setattr(new_holder, reverse_attr_name, instance)
            if fit is not None:
                fit._add_holder(new_holder)
                fit._request_volatile_cleanup()
