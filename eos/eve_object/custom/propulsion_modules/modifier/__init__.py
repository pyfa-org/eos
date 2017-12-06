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


from .dogma import make_mass_modifier
from .dogma import make_signature_modifier
from .python import PropulsionModuleVelocityBoostModifier


_ab_modifiers = None
_mwd_modifiers = None


def get_ab_modifiers():
    global _ab_modifiers
    if _ab_modifiers is None:
        _ab_modifiers = (
            PropulsionModuleVelocityBoostModifier(),
            make_mass_modifier())
    return _ab_modifiers


def get_mwd_modifiers():
    global _mwd_modifiers
    if _mwd_modifiers is None:
        _mwd_modifiers = (
            *get_ab_modifiers(),
            make_signature_modifier())
    return _mwd_modifiers
