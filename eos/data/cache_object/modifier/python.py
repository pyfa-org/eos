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


from abc import ABCMeta, abstractmethod

from eos.util.repr import make_repr_str
from .base import BaseModifier


class BasePythonModifier(BaseModifier, metaclass=ABCMeta):
    """
    Python modifiers offer more capabilities than dogma modifiers,
    but it comes at performance cost.
    """

    def __init__(
            self, state=None, tgt_filter=None, tgt_domain=None,
            tgt_filter_extra_arg=None, tgt_attr=None
    ):
        BaseModifier.__init__(
            self, state=state, tgt_filter=tgt_filter, tgt_domain=tgt_domain,
            tgt_filter_extra_arg=tgt_filter_extra_arg, tgt_attr=tgt_attr
        )

    @property
    @abstractmethod
    def trigger_message_types(self):
        """
        Return iterable with message types this modifier wants
        to receive.
        """
        ...

    @abstractmethod
    def is_triggered(self, message, carrier_item, fit):
        """
        Take message and additional context arguments to determine
        if changing them affects attribute targeted by modifier.
        Result is boolean value.
        """
        ...

    # Auxiliary methods
    def __repr__(self):
        return make_repr_str(self)
