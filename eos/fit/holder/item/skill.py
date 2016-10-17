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


from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.mixin.state import ImmutableStateMixin
from eos.util.repr import make_repr_str


class Skill(ImmutableStateMixin):
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
        self.__level = None
        super().__init__(type_id=type_id, state=State.offline, **kwargs)
        self.level = level

    @property
    def _domain(self):
        return Domain.character

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, value):
        value = int(value)
        # Skip everything if level isn't actually
        # changed
        if self.__level == value:
            return
        self.__level = value
        # Clear everything relying on skill level,
        # if skill is assigned to fit
        fit = self._fit
        if fit is not None:
            fit._request_volatile_cleanup()
            fit._link_tracker.clear_holder_attribute_dependents(self, Attribute.skill_level)

    def __repr__(self):
        spec = [['type_id', '_type_id'], 'level']
        return make_repr_str(self, spec)
