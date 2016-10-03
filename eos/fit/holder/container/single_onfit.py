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


from eos.fit.exception import HolderAlreadyAssignedError
from .base import HolderContainerBase


class HolderDescriptorOnFit(HolderContainerBase):
    """
    Container for single holder, intended to be used
    as fit attribute for direct access.

    Required arguments:
    attr_name -- name of instance attribute which
    should be used to store data processed by descriptor
    holder_class -- class of holders this container
    is allowed to contain
    """

    def __init__(self, attr_name, holder_class):
        HolderContainerBase.__init__(self, holder_class)
        self.__attr_name = attr_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.__attr_name, None)

    def __set__(self, instance, new_holder):
        self._check_class(new_holder, allow_none=True)
        attr_name = self.__attr_name
        old_holder = getattr(instance, attr_name, None)
        if old_holder is not None:
            instance._request_volatile_cleanup()
            instance._remove_holder(old_holder)
        setattr(instance, attr_name, new_holder)
        if new_holder is not None:
            try:
                instance._add_holder(new_holder)
            except HolderAlreadyAssignedError as e:
                setattr(instance, attr_name, old_holder)
                if old_holder is not None:
                    instance._add_holder(old_holder)
                raise ValueError(*e.args) from e
            instance._request_volatile_cleanup()
