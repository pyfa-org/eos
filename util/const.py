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

import math

# Item categories
catShip = 6
catCharge = 8
catSkill = 16
catImplant = 20
catSubsystem = 32
# Item categories immune to stacking penalty
penaltyImmuneCats = (catShip, catCharge, catSkill,
                     catImplant, catSubsystem)
# Stacking penalty base constant
penaltyBase = 1 / math.exp((1 / 2.67) ** 2)
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
# Dogma operands section
opndAIM = 6  # Add Item Modifier, applies modification directly to some item, format: ((location->targetAttribute).(operation)).AIM(sourceAttribute)
opndALGM = 7  # Add location group modifier, applies modification to items belonging to some location, filtered by group, format: ((location..groupFilter->targetAttribute).(operation)).ALGM(sourceAttribute)
opndALM = 8  # Add location modifier, applies modification to all items belonging to some location, format: ((location->targetAttribute).(operation)).ALM(sourceAttribute)
opndAtt = 12  # Joins location and attribute, format:
opndCombine = 17  # Executes two statements
opndDefAssociation = 21  # Define attribute association type (operator)
opndDefAttribute = 22  # Define attribute
opndDefEnvIdx = 24  # Define environment index
opndDefGroup = 26  # Define group
opndDefInt = 27  # Defines an int constant
opndDefTypeId = 29  # Define a type ID
opndEff = 31  # Define association type (joins target attribute of entity and operation)
opndLG = 48  # Specify a group in a location
opndLS = 49  # Location - skill required item group
