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


from eos.exception import EosError


__all__ = [
    'UnknownStateError',
    'UnknownOperatorError',
    'UnknownFuncError',
    'NoFilterValueError',
    'UnexpectedDomainError',
    'UnexpectedBuilderError'
]


# Exception classes used by converter which uses modifier
# info as source for modifier data
class ModifierInfoCnvError(EosError):
    """
    All exceptions raised by modifierInfo-to-modifier
    converter are based on this class.
    """
    pass


class UnknownStateError(ModifierInfoCnvError):
    pass


class UnknownOperatorError(ModifierInfoCnvError):
    pass


class UnknownFuncError(ModifierInfoCnvError):
    pass


class NoFilterValueError(ModifierInfoCnvError):
    pass


class UnexpectedDomainError(ModifierInfoCnvError):
    pass


class UnexpectedBuilderError(ModifierInfoCnvError):
    pass
