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


from .shared import operand_data


class Action:
    """
    Internal modifier builder object, serves as intermediate layer between
    expression tree and final modifier objects. Modifiers are composed out
    of two actions: the one which applies modification and the one which
    undoes it. Action fields contain mix of EVE-specific and Eos-specific
    constants, as only some of them are converted into Eos 'format' when
    building action.
    """

    def __init__(self):
        # Type of action, must be eos.const.eve.Operand class'
        # attribute value, only those which describe some operation
        # applied onto item.
        self.type = None

        # Which attribute's data will be used as source data for action,
        # must be integer which refers attribute via ID.
        self.src_attr = None

        # Which operation should be applied onto target attribute,
        # must be eos.const.eos.Operator class' attribute value.
        self.operator = None

        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.tgt_attr = None

        # Target domain to change:
        # For action types belonging to gang group, must be None
        # For other action types must be eos.const.eos.Domain
        # class' attribute value.
        self.domain = None

        # Items only belonging to this group will be affected by action:
        # For action types which include group filter, must be integer
        # which refers group via ID;
        # For other action types must be None.
        self.tgt_group = None

        # Items only having this skill requirement will be targeted by
        # action:
        # For action types which include skill requirement filter,
        # must be integer which refers type via ID
        # For other action types must be None.
        self.tgt_skillrq = None

        # For action types which include skill requirement filter,
        # set to true if required skill is carrier of modification
        self.tgt_skillrq_self = False

    def is_mirror(self, other):
        """
        Check if passed action is mirrored version of self.

        Required arguments:
        other -- action to check against

        Return value:
        True if both actions do the same, with the exception that
        one of them applies something and another one undoes it,
        else false
        """
        # Check types which must be mirrorred
        try:
            self_action_data = operand_data[self.type]
        except KeyError:
            self_action_mirror = None
        else:
            self_action_mirror = self_action_data.mirror
        if self_action_mirror != other.type:
            return False
        # Then, check all other fields of modifier
        if (
            self.src_attr != other.src_attr or
            self.operator != other.operator or
            self.tgt_attr != other.tgt_attr or
            self.domain != other.domain or
            self.tgt_group != other.tgt_group or
            self.tgt_skillrq != other.tgt_skillrq or
            self.tgt_skillrq_self is not other.tgt_skillrq_self
        ):
            return False
        # If all conditions were met, then it's actually mirror
        return True
