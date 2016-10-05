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


# This should NOT be above the imports but there is a circular import to be solved first
__version__ = '0.0.0.dev3'  # NOQA

from .const.eos import State, Restriction
from .data.cache_handler.exception import TypeFetchError
from .data.source import SourceManager
from .fit import Fit
from .fit.restriction_tracker.exception import ValidationError
from .fit.tuples import DamageTypes
from .data.data_handler import JsonDataHandler, SQLiteDataHandler
from .data.cache_handler import JsonCacheHandler
from .fit.holder.item import (
    Booster, Character, Drone, Charge, EffectBeacon, Implant,
    ModuleHigh, ModuleMed, ModuleLow, Rig, Ship, Skill, Stance, Subsystem
)

__all__ = [
    'State',
    'Restriction',
    'TypeFetchError',
    'SourceManager',
    'Fit',
    'ValidationError',
    'DamageTypes',
    'JsonDataHandler',
    'SQLiteDataHandler',
    'JsonCacheHandler',
    'Booster',
    'Character',
    'Charge',
    'Drone',
    'EffectBeacon',
    'Implant',
    'ModuleHigh',
    'ModuleMed',
    'ModuleLow',
    'Rig',
    'Ship',
    'Skill',
    'Stance',
    'Subsystem',
]
