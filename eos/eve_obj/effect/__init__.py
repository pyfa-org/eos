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


from .dmg_dealer import load_dmg_dealers
from .cap_transmit import load_cap_transmit
from .effect import Effect
from .ewar import load_ewar
from .factory import EffectFactory
from .neut import load_neuts
from .repairs import load_repairers
from .warfare_buff import load_warfare_buffs


load_cap_transmit()
load_dmg_dealers()
load_ewar()
load_neuts()
load_repairers()
load_warfare_buffs()
