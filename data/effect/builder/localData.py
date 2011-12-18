#===============================================================================
# Copyright (C) 2011 Diego Duclos
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

from eos import const

# Mirror duration modifications, top-level operands
mirrorDurationMods = {const.opndAddGangGrpMod: const.opndRmGangGrpMod,
                      const.opndAddGangItmMod: const.opndRmGangItmMod,
                      const.opndAddGangOwnSrqMod: const.opndRmGangOwnSrqMod,
                      const.opndAddGangSrqMod: const.opndRmGangSrqMod,
                      const.opndAddItmMod: const.opndRmItmMod,
                      const.opndAddLocGrpMod: const.opndRmLocGrpMod,
                      const.opndAddLocMod: const.opndRmLocMod,
                      const.opndAddLocSrqMod: const.opndRmLocSrqMod,
                      const.opndAddOwnSrqMod: const.opndRmOwnSrqMod}
# Plain duration modifications list
durationMods = set(mirrorDurationMods.keys()).union(set(mirrorDurationMods.values()))

# List of instant modification operands
instantMods = {const.opndAssign, const.opndInc, const.opndDec}
