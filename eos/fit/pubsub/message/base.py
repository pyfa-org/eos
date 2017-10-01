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


"""
There're two message types in eos: input messages and instructions. Input messages
are always generated as consequence of user activity, one per change he makes.
One such input message can lead to generation of multiple instructions. Services
listen to message types according to their needs.
"""


from abc import ABCMeta, abstractmethod

from eos.util.repr import make_repr_str


class BaseInputMessage(metaclass=ABCMeta):
    """
    Base class for all input messages.
    """

    @abstractmethod
    def get_instructions(self):
        ...

    def __repr__(self):
        return make_repr_str(self, ())


class BaseInstructionMessage:
    """
    Base class for all instruction messages.
    """

    def __repr__(self):
        return make_repr_str(self, ())
