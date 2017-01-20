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

from eos.const.eos import State, ModifierScope, ModifierDomain, ModifierOperator
from eos.util.repr import make_repr_str


class BaseModifier(metaclass=ABCMeta):
    """
    Modifiers are part of effects; one modifier describes one
    modification - when it should be applied, on which items,
    how to apply it, and so on.
    """

    def __init__(self, id_, scope, domain, state, src_attr, operator, tgt_attr):
        self.id = id_
        self.scope = scope
        self.domain = domain
        self.state = state
        self.src_attr = src_attr
        self.operator = operator
        self.tgt_attr = tgt_attr

    @property
    @abstractmethod
    def type(self):
        ...

    @abstractmethod
    def _validate(self):
        ...

    def _validate_basic_attrs(self):
        return all((
            isinstance(self.id, int) or self.id is None,
            self.scope in ModifierScope.__members__.values(),
            self.domain in ModifierDomain.__members__.values(),
            self.state in State.__members__.values(),
            isinstance(self.src_attr, int),
            self.operator in ModifierOperator.__members__.values(),
            isinstance(self.tgt_attr, int)
        ))

    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
