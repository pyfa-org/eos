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


from eos.const.eos import ModDomain
from eos.const.eos import State
from eos.const.eve import AttrId
from eos.util.repr import make_repr_str
from .mixin.state import ImmutableStateMixin


class Skill(ImmutableStateMixin):
    """Represents a skill.

    Args:
        type_id: Identifier of item type which should serve as base for this
            skill.
        level (optional): Sets level of skill at initialization, default is 0.
    """

    def __init__(self, type_id, level=0):
        super().__init__(type_id=type_id, state=State.offline)
        self.__level = level
        self.attrs._set_override_callback(
            AttrId.skill_level, (getattr, (self, 'level'), {}))

    @property
    def level(self):
        """Access point to skill level."""
        return self.__level

    @level.setter
    def level(self, new_lvl):
        old_lvl = self.__level
        if new_lvl == old_lvl:
            return
        self.__level = new_lvl
        self.attrs._override_value_may_change(AttrId.skill_level)

    # Attribute calculation-related properties
    _modifier_domain = ModDomain.character
    _owner_modifiable = False

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id'], 'level']
        return make_repr_str(self, spec)
