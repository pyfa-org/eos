#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
#===============================================================================


from eos.exception import EosException


class AttributeCalculatorException(EosException):
    """All attribute calculator exceptions are based on this class."""
    pass


# Exception classes used by link register
class DirectLocationError(AttributeCalculatorException):
    """
    Raised when location in Info object being processed cannot be
    handled by register (set of unsupported locations is different
    for direct and filtered modifications).
    """
    pass


class FilteredLocationError(AttributeCalculatorException):
    """
    Raised when location in Info object being processed cannot be
    handled by register (set of unsupported locations is different
    for direct and filtered modifications).
    """
    pass


class FilteredSelfReferenceError(AttributeCalculatorException):
    """
    Raised when info references itself as holder container, but
    actually it can't have any holders assigned to it.
    """
    pass


class FilterTypeError(AttributeCalculatorException):
    """
    Raised when info specifies uknown to calculator filter type.
    """
    pass


# Exception classes used by map's calculation method
class BaseValueError(AttributeCalculatorException):
    """
    Raised when value, upon which attribute calculation should be based,
    cannot be determined, thus making it impossible to calculate attribute.
    """
    pass


class AttributeMetaError(AttributeCalculatorException):
    """
    Raised when attribute being calculated cannot be found in
    attribute database.
    """
    pass


class OperatorError(AttributeCalculatorException):
    """
    Raised during calculation process, if attribute affector is
    using operator which is not supported by calculate method.
    """
    pass


class SourceTypeError(AttributeCalculatorException):
    """
    Raised during calculation process, if source type is unknown
    to calculate method.
    """
    pass
