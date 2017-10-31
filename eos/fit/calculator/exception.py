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


from eos.exception import EosError


class AttributeCalculatorError(EosError):
    """All attribute calculator exceptions are based on this class."""
    ...


# Exception classes used by affection register
class UnexpectedDomainError(AttributeCalculatorError):
    """Raised when modifier domain has unexpected value.

    Raised when modifier being processed cannot have this domain (which domains
    are supported depends on modifier target filter and its context).
    """
    ...


class UnknownTargetFilterError(AttributeCalculatorError):
    """Raised when modifier has unknown target filter type."""
    ...


# Exception classes used by map's calculation method
class AttributeMetadataError(AttributeCalculatorError):
    """Raised when attribute cannot be found in attribute database."""
    ...


class BaseValueError(AttributeCalculatorError):
    """Raised when base value of attribute cannot be calculated.

    WHen calculating modified value of an attribute, we can take initial value
    from the item or from default value of the attribute. If neither is defined,
    this exception is raised.
    """
    ...
