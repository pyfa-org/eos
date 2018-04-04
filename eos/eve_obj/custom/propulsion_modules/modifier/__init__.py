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


from .dogma import make_mass_modifier
from .dogma import make_signature_modifier
from .python import PropulsionModuleVelocityBoostModifier


def make_ab_modifiers():
    ab_modifiers = (
        PropulsionModuleVelocityBoostModifier(),
        make_mass_modifier())
    return ab_modifiers


def make_mwd_modifiers():
    mwd_modifiers = (
        *make_ab_modifiers(),
        make_signature_modifier())
    return mwd_modifiers
