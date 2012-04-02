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


from .helpers import operandData


class Action:
    """
    Internal modifier builder object, serves as intermediate layer between
    expression tree and final modifier objects. Modifiers are composed out
    of two actions: the one which applies modification and the one which
    undoes it. Action values contain mix of EVE-specific and Eos-specific
    constants, as only some of them are converted into Eos 'format' when
    building action.
    """

    def __init__(self):
        # Type of action, must be eos.eve.const.Operand class'
        # attribute value, only those which describe some operation
        # applied onto item.
        self.type = None

        # Which attribute's data will be used as source data for action,
        # must be integer which refers attribute via ID.
        self.sourceAttributeId = None

        # Which operation should be applied onto target attribute,
        # must be eos.const.Operator class' attribute value.
        self.operator = None

        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.targetAttributeId = None

        # Target location to change:
        # For action types belonging to gang group, must be None
        # For other action types must be eos.const.Location
        # class' attribute value.
        self.targetLocation = None

        # Items only belonging to this group will be affected by action:
        # For action types which include group filter, must be integer
        # which refers group via ID;
        # For other action types must be None.
        self.targetGroupId = None

        # Items only having this skill requirement will be targeted by
        # action:
        # For action types which include skill requirement filter,
        # must be integer which refers type via ID, or
        # eos.const.InvType.self_ to refer type of effect carrier
        # For other action types must be None.
        self.targetSkillRequirementId = None


    def isMirror(self, other):
        """
        Check if passed action is mirrored version of self.

        Positional arguments:
        other -- action to check against

        Return value:
        True if both actions do the same, with the exception that
        one of them applies something and another one undoes it,
        else false
        """
        # Check types which must be mirror
        try:
            selfActionData = operandData[self.type]
        except KeyError:
            selfActionMirror = None
        else:
            selfActionMirror = selfActionData.mirror
        if selfActionMirror != other.type:
            return False
        # Then, check all other fields of modifier
        if (self.sourceAttributeId != other.sourceAttributeId or self.operator != other.operator or
            self.targetAttributeId != other.targetAttributeId or self.targetLocation != other.targetLocation or
            self.targetGroupId != other.targetGroupId or self.targetSkillRequirementId != other.targetSkillRequirementId):
            return False
        # If all conditions were met, then it's actually mirror
        return True
