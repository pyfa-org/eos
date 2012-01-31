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


from .operandData import operandData, OperandType


class Modifier:
    """
    Internal builder object, stores meaningful elements of expression tree
    temporarily and provides facilities to convert them to Info objects
    """

    def __init__(self):
        # Conditions under which modification is applied,
        # must be None or tree of condition Atom objects.
        self.conditions = None
        # Type of modification, must be Operand class' attribute value,
        # only those which describe some operation applied onto item
        # (belonging to either durationMods orinstantMods sets).
        self.type = None
        # Keeps category ID of effect from whose expressions it
        # was generated
        self.effectCategoryId = None
        # Describes when modification should be applied, for instant
        # modifications only:
        # For modifier types, belonging to instant, must be
        # InfoRunTime.pre or InfoRunTime.post;
        # For other modifier types, must be None.
        self.runTime = None
        # Target location to change:
        # For modifier types belonging to gang group, must be None
        # For other modifier types must be InfoLocation class'
        # attribute value.
        self.targetLocation = None
        # Which operation should be applied during modification,
        # must be InfoOperator class' attribute value.
        self.operator = None
        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.targetAttributeId = None
        # Items only belonging to this group will be affected by
        # modification:
        # For modifier types, which include group filter, must be integer
        # which refers group via ID;
        # For other modifier types must be None.
        self.targetGroupId = None
        # Items only having this skill requirement will be affected by
        # modification:
        # For modifier types, which include skill requirement filter,
        # must be integer which refers type via ID, or const.Type.self_
        # to refer type of info carrier
        # For other modifier types must be None.
        self.targetSkillRequirementId = None
        # SourceValue type, must be InfoSourceType class'
        # attribute value.
        self.sourceType = None
        # Value which is used as modification value for operation:
        # For sourceType.attribute must be integer which refers attribute via ID;
        # For sourceType.value must be any value CCP can define in expression, integer or value.
        self.sourceValue = None

    @classmethod
    def isSameMod(cls, mod1, mod2):
        """
        Check if both duration modifiers actually do the same thing

        Positional arguments:
        mod1 -- first modifier to check
        mod2 -- second modifier to check

        Return value:
        True if both modifiers are duration and all their duration-related
        attributes are the same, else False
        """
        # Check if both are duration modifiers
        for modifier in {mod1, mod2}:
            try:
                modData = operandData[modifier.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.duration:
                return False
        # Check all modifier fields that make the difference for duration modifiers
        if (mod1.type != mod2.type or mod1.effectCategoryId != mod2.effectCategoryId or
            mod1.sourceType != mod2.sourceType or mod1.sourceValue != mod2.sourceValue or
            mod1.operator != mod2.operator or mod1.targetAttributeId != mod2.targetAttributeId or
            mod1.targetLocation != mod2.targetLocation or mod1.targetGroupId != mod2.targetGroupId or
            mod1.targetSkillRequirementId != mod2.targetSkillRequirementId):
            return False
        # They're the same if above conditions were passed, other fields irrelevant
        return True
