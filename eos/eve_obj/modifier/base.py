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

from eos.const.eos import ModDomain
from eos.const.eos import ModTgtFilter


class BaseModifier(metaclass=ABCMeta):
    """Define base functionality for all modifier types.

    Modifiers are part of effects; one modifier describes one modification -
    when it should be applied, on which items, how to apply it, and so on.
    """

    def __init__(
            self, tgt_filter, tgt_domain, tgt_filter_extra_arg, tgt_attr_id):
        self.tgt_filter = tgt_filter
        self.tgt_domain = tgt_domain
        self.tgt_filter_extra_arg = tgt_filter_extra_arg
        self.tgt_attr_id = tgt_attr_id

    @abstractmethod
    def get_modification(self, mod_item):
        """Get modification parameters.

        Args:
            mod_item: Item which carries the modifier.

        Returns:
            Tuple (operator, modification value) which is intermediate result of
            applying modification - only first half of process is complete, when
            modification source value is calculated and operator is defined.

        """
        ...

    # Validation-related methods
    def _validate_base(self):
        tgt_validators = {
            ModTgtFilter.item:
                self.__validate_tgt_filter_item,
            ModTgtFilter.domain:
                self.__validate_tgt_filter_domain,
            ModTgtFilter.domain_group:
                self.__validate_tgt_filter_domain_group,
            ModTgtFilter.domain_skillrq:
                self.__validate_tgt_filter_domain_skillrq,
            ModTgtFilter.owner_skillrq:
                self.__validate_tgt_filter_owner_skillrq}
        try:
            tgt_validator = tgt_validators[self.tgt_filter]
        except KeyError:
            return False
        else:
            return all((
                self.__validate_tgt_common(),
                tgt_validator()))

    def __validate_tgt_common(self):
        return all((
            self.tgt_filter in ModTgtFilter.__members__.values(),
            self.tgt_domain in ModDomain.__members__.values(),
            isinstance(self.tgt_attr_id, Integral)))

    def __validate_tgt_filter_item(self):
        return all((
            self.tgt_domain in (
                ModDomain.self, ModDomain.character, ModDomain.ship,
                ModDomain.target, ModDomain.other),
            self.tgt_filter_extra_arg is None))

    def __validate_tgt_filter_domain(self):
        return all((
            self.tgt_domain in (
                ModDomain.self, ModDomain.character,
                ModDomain.ship, ModDomain.target),
            self.tgt_filter_extra_arg is None))

    def __validate_tgt_filter_domain_group(self):
        return all((
            self.tgt_domain in (
                ModDomain.self, ModDomain.character,
                ModDomain.ship, ModDomain.target),
            # References group via ID
            isinstance(self.tgt_filter_extra_arg, Integral)))

    def __validate_tgt_filter_domain_skillrq(self):
        return all((
            self.tgt_domain in (
                ModDomain.self, ModDomain.character,
                ModDomain.ship, ModDomain.target),
            # References skill via ID
            isinstance(self.tgt_filter_extra_arg, Integral)))

    def __validate_tgt_filter_owner_skillrq(self):
        return all((
            self.tgt_domain == ModDomain.character,
            # References skill via ID
            isinstance(self.tgt_filter_extra_arg, Integral)))
