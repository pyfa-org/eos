#===============================================================================
# Copyright (C) 2011 Anton Vorobyov
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

# Dogma operators section, here we deliberately assign IDs,
# but make sure IDs are assigned to keep operations in
# proper order
operPreAssignment = 1
operPreMul = 2
operPreDiv = 3
operModAdd = 4
operModSub = 5
operPostMul = 6
operPostDiv = 7
operPostPercent = 8
operPostAssignment = 9
# Database name: ID map for Dogma operators
operConvMap = {"PreAssignment": operPreAssignment,
               "PreMul": operPreMul,
               "PreDiv": operPreDiv,
               "ModAdd": operModAdd,
               "ModSub": operModSub,
               "PostMul": operPostMul,
               "PostDiv": operPostDiv,
               "PostPercent": operPostPercent,
               "PostAssignment": operPostAssignment}
