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

# Attributes
attrSkillRq1 = 182
attrSkillRq2 = 183
attrSkillRq3 = 184
attrSkillRq1Lvl = 277
attrSkillRq2Lvl = 278
attrSkillRq3Lvl = 279
attrSkillRq4 = 1285
attrSkillRq4Lvl = 1286
attrSkillRq5Lvl = 1287
attrSkillRq6Lvl = 1288
attrSkillRq5 = 1289
attrSkillRq6 = 1290
# Dictionary which holds skill requirement attribute IDs
# and their corresponding level attribute IDs
attrSkillRqMap = {attrSkillRq1: attrSkillRq1Lvl,
                  attrSkillRq2: attrSkillRq2Lvl,
                  attrSkillRq3: attrSkillRq3Lvl,
                  attrSkillRq4: attrSkillRq4Lvl,
                  attrSkillRq5: attrSkillRq5Lvl,
                  attrSkillRq6: attrSkillRq6Lvl}

# Item categories
catShip = 6
catCharge = 8
catSkill = 16
catImplant = 20
catSubsystem = 32

# Item categories immune to stacking penalty
penaltyImmuneCats = {catShip, catCharge, catSkill,
                     catImplant, catSubsystem}
# Stacking penalty base constant
penaltyBase = 1 / math.exp((1 / 2.67) ** 2)

# Dogma operands section
opndAddGangGrpMod = 2  # Applies modification to items of gang-mates, filtered by group, format: [(groupFilter.targetAttribute).(operator)].AGGM(sourceAttribute)
opndAddGangItmMod = 3  # Applies modification directly to ships gang-mates, format: ((targetAttribute).(operator)).AGIM(sourceAttribute)
opndAddGangOwnSrqMod = 4  # Applies modification to items of gang-mates, filtered by owner and skill requirement
opndAddGangSrqMod = 5  # Applies modification to items of gang-mates, filtered by skill requirement, format: (skillRequirement.targetAttribute).(operator)).AGRSM(sourceAttribute))
opndAddItmMod = 6  # Applies modification directly to some item, format: ((location->targetAttribute).(operator)).AIM(sourceAttribute)
opndAddLocGrpMod = 7  # Applies modification to items belonging to some location, filtered by group, format: ((location..groupFilter->targetAttribute).(operator)).ALGM(sourceAttribute)
opndAddLocMod = 8  # Applies modification to all items belonging to some location, format: ((location->targetAttribute).(operator)).ALM(sourceAttribute)
opndAddLocSrqMod = 9  # Applies modification to items belonging to some location, filtered by skill requirement, format: ((location[skillRequirement]->targetAttribute).(operator)).ALRSM(sourceAttribute)
opndAddOwnSrqMod = 11  # Applies modification to items belonging to some location, filtered by owner of source, format: ((location[skillRequirement]->targetAttribute).(operator)).AORSM(sourceAttribute)
opndItmAttr = 12  # Joins target items and attribute into target definition, format: location->targetAttribute
opndAttack = 13  # Special operand, handles turret attack
opndCargoScan = 14  # Special operand, used to define cargo scan
opndCheatTeleDock = 15  # Special operand, handles GM tools
opndCheatTeleGate = 16  # Special operand, handles GM tools
opndSplice = 17  # Executes two statements, format: expression1; expression2
opndDec = 18  # Decreases value for some attribute by value of another one
opndAoeDecloak = 19  # Special operand, defines area-of-effect decloak
opndDefOptr = 21  # Define operator, text in expressionValue field
opndDefAttr = 22  # Define attribute, integer in expressionAttributeID field
opndDefBool = 23  # Define boolean constant, boolean in expressionValue field
opndDefLoc = 24  # Define location, text in expressionValue field
opndDefGrp = 26  # Define group, integer in expressionGroupID field
opndDefInt = 27  # Defines an integer constant, integer in expressionValue field
opndDefType = 29  # Define a type, integer in expressionTypeID field
opndEcmBurst = 30  # Special operand, used in ECM Burst effects
opndOptrTgt = 31  # Joins operator and target (attribute of possibly filtered items) definitions, format: (location->targetAttribute).(operator)
opndAoeDmg = 32  # Special operand, defines area-of-effect damage for modules like smartbombs and old doomsday
opndGrpAttr = 34  # Joins group and attribute into target definition, format: groupFilter.targetAttribute
opndGetType = 36  # Gets type of item in arg1
opndGenAttr = 40  # Generic attribute reference, doesn't join anything, just references attribute definition
opndInc = 42  # Increases value of some attribute by the value of another one
opndMissileLaunch = 44  # Special operand, handles missile launching
opndDefenderLaunch = 45  # Special operand, handles defender missile launching
opndFofLaunch = 47  # Special operand, handles friend-or-foe missile launching
opndLocGrp = 48  # Joins location and group definitions into single filter, format: location..group
opndLocSrq = 49  # Joins location and skill requirement definitions into single filter, format: location[skillRequirement]
opndMine = 50  # Special operand, handles transfer of ore from asteroid to cargo
opndPowerBooster = 53  # Special operand, defines cap booster effect
opndRmGangGrpMod = 54  # Undos modification from items of gang-mates, filtered by group, format: [(groupFilter.targetAttribute).(operator)].RGGM(sourceAttribute)
opndRmGangItmMod = 55  # Undos modification directly from ships gang-mates, format: ((targetAttribute).(operator)).RGIM(sourceAttribute)
opndRmGangOwnSrqMod = 56  # Undos modification from items of gang-mates, filtered by owner and skill requirement
opndRmGangSrqMod = 57  # Undos modification from items of gang-mates, filtered by skill requirement, format: (skillRequirement.targetAttribute).(operator)).RGRSM(sourceAttribute))
opndRmItmMod = 58  # Undos modification directly from some item, format: ((location->targetAttribute).(operator)).RIM(sourceAttribute)
opndRmLocGrpMod = 59  # Undos modification from items belonging to some location, filtered by group, format: ((location..groupFilter->targetAttribute).(operator)).RLGM(sourceAttribute)
opndRmLocMod = 60  # Undos modification from all items belonging to some location, format: ((location->targetAttribute).(operator)).RLM(sourceAttribute)
opndRmLocSrqMod = 61  # Undos modification from items belonging to some location, filtered by skill requirement, format: ((location[skillRequirement]->targetAttribute).(operator)).RLRSM(sourceAttribute)
opndRmOwnSrqMod = 62  # Undos modification from items belonging to some location, filtered by owner of source, format: ((location[skillRequirement]->targetAttribute).(operator)).RORSM(sourceAttribute)
opndSrqAttr = 64  # Joins skill requirement and attribute into target definition, format: skillRequirement.targetAttribute
opndAssign = 65  # Direct assignment to one attribute value of another one
opndShipScan = 66  # Special operand, used to define ship scan
opndSurveyScan = 69  # Special operand, used to define ore scan
opndTgtHostile = 70  # Special operand, used in auto-targeting systems
opndTgtSilent = 71  # Special operand, used in passive targeting systems
opndToolTgtSkills = 72  # Special operand, most likely checks if you have enough skills to use currently loaded charge, or have enough skills to work with current target
opndVrfTgtGrp = 74  # Special operand, used to verify if target can have effect's carrier applied onto it, otherwise raises error


### Custom Eos stuff, doesn't depend on database IDs ###

# Dogma operators section, here we deliberately assign IDs,
# but make sure IDs are assigned to keep operations in
# proper order
optrPreAssignment = 1
optrPreMul = 2
optrPreDiv = 3
optrModAdd = 4
optrModSub = 5
optrPostMul = 6
optrPostDiv = 7
optrPostPercent = 8
optrPostAssignment = 9
# Following operators are for immediate modification
optrIncr = 10
optrDecr = 11
optrAssign = 12

# Database name: ID map for Dogma operators
optrConvMap = {"PreAssignment": optrPreAssignment,
               "PreMul": optrPreMul,
               "PreDiv": optrPreDiv,
               "ModAdd": optrModAdd,
               "ModSub": optrModSub,
               "PostMul": optrPostMul,
               "PostDiv": optrPostDiv,
               "PostPercent": optrPostPercent,
               "PostAssignment": optrPostAssignment}

# Target location IDs
locSelf = 1  # Target self, i.e. carrier of modification source
locChar = 2  # Target character
locShip = 3  # Target ship
locTgt = 4  # Target currently locked and selected ship as target
locOther = 5  # If used from charge, targets charge's container, is used from container, targets its charge
locArea = 6  # No detailed data about this one, according to expressions, it affects everything on grid (the only expression using it is area-of-effect repair, but it's not assigned to any effects)
locSpace = 7  # Target stuff in space (e.g. your launched drones and missiles); this location is Eos-specific and not taken from EVE

# Database name: ID map for target locations
locConvMap = {"Self": locSelf,
              "Char": locChar,
              "Ship": locShip,
              "Target": locTgt,
              "Other": locOther,
              "Area": locArea}

# Filter types
filterAll = 1
filterGroup = 2
filterSkill = 3

# Effect info types
infoDuration = 1
infoPre = 2
infoPost = 3

# Self type getter ID
selfTypeID = -1
