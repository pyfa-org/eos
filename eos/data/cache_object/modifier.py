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


from eos.const.eos import State, Domain, Operator
from eos.util.repr import make_repr_str


class BaseModifier:
    """
    Modifiers are part of effects; one modifier describes one
    modification - when it should be applied, on which items,
    how to apply it, and so on.
    """

    def __init__(self, id, src_attr, operator, tgt_attr, state, domain):
        self.id = id
        self.src_attr = src_attr
        self.operator = operator
        self.tgt_attr = tgt_attr
        self.state = state
        self.domain = domain

    def _validate(self):
        return all((
            isinstance(self.id, int) or self.id is None,
            isinstance(self.src_attr, int),
            self.operator in Operator.__members__.values(),
            isinstance(self.tgt_attr, int),
            self.state in State.__members__.values(),
            self.domain in Domain.__members__.values()
        ))

    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)


class ItemModifier(BaseModifier):
    """
    Affects single item specified in domain.
    """

    def _validate(self):
        return all((
            super()._validate(),
            self.domain in (Domain.self_, Domain.character, Domain.ship, Domain.target, Domain.other)
        ))


class LocationModifier(BaseModifier):
    """
    Affects all items which belong to location
    specified on domain.
    """

    def _validate(self):
        return all((
            super()._validate(),
            self.domain in (Domain.self_, Domain.character, Domain.ship, Domain.target)
        ))


class LocationGroupModifier(BaseModifier):
    """
    Affects all items which belong to location
    specified on domain and to specified group.
    """

    def __init__(self, id, src_attr, operator, tgt_attr, state, domain, group):
        super().__init__(id, src_attr, operator, tgt_attr, state, domain)
        self.group = group

    def _validate(self):
        return all((
            super()._validate(),
            isinstance(self.group, int),
            self.domain in (Domain.self_, Domain.character, Domain.ship, Domain.target)
        ))


class LocationRequiredSkillModifier(BaseModifier):
    """
    Affects all items which belong to location specified
    on domain and have specified skill requirement.
    """

    def __init__(self, id, src_attr, operator, tgt_attr, state, domain, skill):
        super().__init__(id, src_attr, operator, tgt_attr, state, domain)
        self.skill = skill

    def _validate(self):
        return all((
            super()._validate(),
            isinstance(self.skill, int),
            self.domain in (Domain.self_, Domain.character, Domain.ship, Domain.target)
        ))


class OwnerRequiredSkillModifier(BaseModifier):
    """
    Affects all items which are owner-modifiable
    and have specified skill requirement.
    """

    def __init__(self, id, src_attr, operator, tgt_attr, state, domain, skill):
        super().__init__(id, src_attr, operator, tgt_attr, state, domain)
        self.skill = skill

    def _validate(self):
        return all((
            super()._validate(),
            isinstance(self.skill, int),
            self.domain in (Domain.ship, Domain.target)
        ))
