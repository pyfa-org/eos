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


from eos.const import Operand


# Mirror duration modifications, top-level operands
# Format: {addition operand: removal operand}
mirrorDurationMods = {Operand.addGangGrpMod: Operand.rmGangGrpMod,
                      Operand.addGangItmMod: Operand.rmGangItmMod,
                      Operand.addGangOwnSrqMod: Operand.rmGangOwnSrqMod,
                      Operand.addGangSrqMod: Operand.rmGangSrqMod,
                      Operand.addItmMod: Operand.rmItmMod,
                      Operand.addLocGrpMod: Operand.rmLocGrpMod,
                      Operand.addLocMod: Operand.rmLocMod,
                      Operand.addLocSrqMod: Operand.rmLocSrqMod,
                      Operand.addOwnSrqMod: Operand.rmOwnSrqMod}
# Plain duration modifications set
durationMods = set(mirrorDurationMods.keys()).union(set(mirrorDurationMods.values()))

# Set of instant modification operands
instantMods = {Operand.assign, Operand.inc, Operand.dec}
