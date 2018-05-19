# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from abc import ABCMeta
from abc import abstractmethod
from numbers import Integral

from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModDomain


class BaseModifier(metaclass=ABCMeta):
    """Define base functionality for all modifier types.

    Modifiers are part of effects; one modifier describes one modification -
    when it should be applied, on which items, how to apply it, and so on.
    """

    def __init__(
        self,
        affectee_filter,
        affectee_filter_extra_arg,
        affectee_domain,
        affectee_attr_id
    ):
        self.affectee_filter = affectee_filter
        self.affectee_filter_extra_arg = affectee_filter_extra_arg
        self.affectee_domain = affectee_domain
        self.affectee_attr_id = affectee_attr_id

    @abstractmethod
    def get_modification(self, affector_item):
        """Get modification parameters.

        Args:
            affector_item: Item which carries the modifier.

        Returns:
            Tuple (operator, modification value) which is intermediate result of
            applying modification - only first half of process is complete, when
            modification source value is calculated and operator is defined.

        """
        ...

    # Validation-related methods
    def _validate_base(self):
        validators = {
            ModAffecteeFilter.item:
                self.__validate_affectee_filter_item,
            ModAffecteeFilter.domain:
                self.__validate_affectee_filter_domain,
            ModAffecteeFilter.domain_group:
                self.__validate_affectee_filter_domain_group,
            ModAffecteeFilter.domain_skillrq:
                self.__validate_affectee_filter_domain_skillrq,
            ModAffecteeFilter.owner_skillrq:
                self.__validate_affectee_filter_owner_skillrq}
        try:
            validator = validators[self.affectee_filter]
        except KeyError:
            return False
        else:
            return all((self.__validate_common(), validator()))

    def __validate_common(self):
        return all((
            self.affectee_filter in ModAffecteeFilter.__members__.values(),
            self.affectee_domain in ModDomain.__members__.values(),
            isinstance(self.affectee_attr_id, Integral)))

    def __validate_affectee_filter_item(self):
        return all((
            self.affectee_filter_extra_arg is None,
            self.affectee_domain in (
                ModDomain.self, ModDomain.character, ModDomain.ship,
                ModDomain.target, ModDomain.other)))

    def __validate_affectee_filter_domain(self):
        return all((
            self.affectee_filter_extra_arg is None,
            self.affectee_domain in (
                ModDomain.self, ModDomain.character,
                ModDomain.ship, ModDomain.target)))

    def __validate_affectee_filter_domain_group(self):
        return all((
            # References group via ID
            isinstance(self.affectee_filter_extra_arg, Integral),
            self.affectee_domain in (
                ModDomain.self, ModDomain.character,
                ModDomain.ship, ModDomain.target)))

    def __validate_affectee_filter_domain_skillrq(self):
        return all((
            # References skill via ID
            isinstance(self.affectee_filter_extra_arg, Integral),
            self.affectee_domain in (
                ModDomain.self, ModDomain.character,
                ModDomain.ship, ModDomain.target)))

    def __validate_affectee_filter_owner_skillrq(self):
        return all((
            # References skill via ID
            isinstance(self.affectee_filter_extra_arg, Integral),
            self.affectee_domain == ModDomain.character))
