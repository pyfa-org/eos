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


from eos.const.eos import State, ModifierDomain
from eos.const.eve import Attribute
from eos.util.repr import make_repr_str
from .base import BaseItem
from .mixin.state import ImmutableStateMixin


class Skill(BaseItem, ImmutableStateMixin):
    """
    Skill with all its special properties.

    Required arguments:
    type_id -- type ID of item which should serve as base
    for this item.

    Optional arguments:
    level -- set level of skill at initialization, default is 0

    Cooperative methods:
    __init__
    """

    def __init__(self, type_id, level=0, **kwargs):
        super().__init__(type_id=type_id, state=State.offline, **kwargs)
        self.level = level

    @property
    def level(self):
        return self.attributes.get(Attribute.skill_level)

    @level.setter
    def level(self, new_lvl):
        self.attributes._override_set(Attribute.skill_level, int(new_lvl), persist=True)

    # Auxiliary methods
    @property
    def _domain(self):
        return ModifierDomain.character

    @property
    def _owner_modifiable(self):
        return False

    def __repr__(self):
        spec = [['type_id', '_type_id'], 'level']
        return make_repr_str(self, spec)
