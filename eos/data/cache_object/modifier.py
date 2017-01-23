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


from eos.const.eos import State, ModifierType, ModifierDomain, ModifierOperator
from eos.util.repr import make_repr_str


class Modifier:
    """
    Modifiers are part of effects; one modifier describes one
    modification - when it should be applied, on which items,
    how to apply it, and so on.
    """

    def __init__(
            self, modifier_id=None, modifier_type=None, domain=None, state=None,
            src_attr=None, operator=None, tgt_attr=None, extra_arg=None
    ):
        self.id = modifier_id
        self.type = modifier_type
        self.domain = domain
        self.state = state
        self.src_attr = src_attr
        self.operator = operator
        self.tgt_attr = tgt_attr
        self.extra_arg = extra_arg

    @property
    def _valid(self):
        validators = {
            ModifierType.item: self.__validate_item_modifer,
            ModifierType.location: self.__validate_location_modifer,
            ModifierType.location_group: self.__validate_location_group_modifer,
            ModifierType.location_skillrq: self.__validate_location_skillrq_modifer,
            ModifierType.owner_skillrq: self.__validate_owner_skillrq_modifer
        }
        try:
            validator = validators[self.type]
        except KeyError:
            return False
        else:
            return validator()

    def __validate_item_modifer(self):
        return all((
            self.__validate_basic_attrs(),
            self.domain in (
                ModifierDomain.self, ModifierDomain.character, ModifierDomain.ship,
                ModifierDomain.target, ModifierDomain.other
            ),
            self.extra_arg is None
        ))

    def __validate_location_modifer(self):
        return all((
            self.__validate_basic_attrs(),
            self.domain in (
                ModifierDomain.self, ModifierDomain.character,
                ModifierDomain.ship, ModifierDomain.target
            ),
            self.extra_arg is None
        ))

    def __validate_location_group_modifer(self):
        return all((
            self.__validate_basic_attrs(),
            self.domain in (
                ModifierDomain.self, ModifierDomain.character,
                ModifierDomain.ship, ModifierDomain.target
            ),
            # References group via ID
            isinstance(self.extra_arg, int)
        ))

    def __validate_location_skillrq_modifer(self):
        return all((
            self.__validate_basic_attrs(),
            self.domain in (
                ModifierDomain.self, ModifierDomain.character,
                ModifierDomain.ship, ModifierDomain.target
            ),
            # References skill via ID
            isinstance(self.extra_arg, int)
        ))

    def __validate_owner_skillrq_modifer(self):
        return all((
            self.__validate_basic_attrs(),
            self.domain == ModifierDomain.character,
            # References skill via ID
            isinstance(self.extra_arg, int)
        ))

    def __validate_basic_attrs(self):
        return all((
            self.type in ModifierType.__members__.values(),
            self.domain in ModifierDomain.__members__.values(),
            self.state in State.__members__.values(),
            isinstance(self.src_attr, int),
            self.operator in ModifierOperator.__members__.values(),
            isinstance(self.tgt_attr, int)
        ))

    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
