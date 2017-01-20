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


class Modifier:
    """
    Modifier objects are Eos-specific abstraction, they replace effects'
    expressions. Each modifier object contains full description of
    modification: when it should be applied, on which items, how to
    apply it, and so on.
    """

    def __init__(
        self,
        modifier_id=None,
        state=None,
        scope=None,
        src_attr=None,
        operator=None,
        tgt_attr=None,
        domain=None,
        filter_type=None,
        filter_value=None
    ):
        # Identifier of modifier, synthesized at
        # cache generation time
        self.id = modifier_id

        # Modifier can be applied only when its carrier holder
        # is in this or greater state, must be const_eos.State
        # class' attribute value.
        self.state = state

        # Describes scope in which modifier is applied, must
        # be const_eos.Scope class' attribute value.
        self.scope = scope

        # Which attribute will be taken as source value,
        # must be integer which refers attribute via ID.
        self.src_attr = src_attr

        # Which operation should be applied during modification,
        # must be const_eos.Operator class' attribute value.
        self.operator = operator

        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.tgt_attr = tgt_attr

        # Target domain to change, must be const_eos.Domain
        # class' attribute value.
        self.domain = domain

        # Filter type of the modification, must be None or
        # const_eos.FilterType class' attribute value.
        self.filter_type = filter_type

        # Filter value of the modification:
        # For filter_type.all_, filter_type.None or filter_type.skill_self must be None;
        # For filter_type.group must be some integer, referring group via ID;
        # For filter_type.skill must be some integer, referring type via ID
        self.filter_value = filter_value

    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)


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
            # TODO: add more checks
        ))


class LocationModifier(BaseModifier):
    """
    Affects all items which belong to location
    specified on domain.
    """

    def _validate(self):
        return all((
            super()._validate(),
            # TODO: add more checks
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
            # TODO: add more checks
        ))


class LocationRequiredSkillModifier(BaseModifier):
    """
    Affects all items which belong to location specified
    on domain and have specified skill requirement.
    """

    def __init__(self, id, src_attr, operator, tgt_attr, state, domain, skill):
        super().__init__(id, src_attr, operator, tgt_attr, state, skill)
        self.skill = skill

    def _validate(self):
        return all((
            super()._validate(),
            isinstance(self.skill, int),
            # TODO: add more checks
        ))


class OwnerRequiredSkillModifier(BaseModifier):
    """
    Affects all items which are owner-modifiable
    and have specified skill requirement.
    """

    def __init__(self, id, src_attr, operator, tgt_attr, state, domain, skill):
        super().__init__(id, src_attr, operator, tgt_attr, state, skill)
        self.skill = skill

    def _validate(self):
        return all((
            super()._validate(),
            isinstance(self.skill, int),
            # TODO: add more checks
        ))
