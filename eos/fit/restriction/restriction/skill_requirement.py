# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.fit.item import Rig, Skill
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


SkillRequirementErrorData = namedtuple(
    'SkillRequirementErrorData', ('skill', 'level', 'required_level'))

EXCEPTIONS = (Rig,)


class SkillRequirementRestrictionRegister(BaseRestrictionRegister):
    """To use item, all its skill requirements must be met.

    Details:
        Only Skill items are able to satisfy skill requirements.
        Item_item type attributes are taken to determine skill and skill level
            requirements.
        If corresponding skill is found, but its skill level is None, check for
            item is failed.
        Rigs are ignored, they can be used regardless of skill requirements.
    """

    def __init__(self, msg_broker):
        self.__skills = {}
        # Set with items which have any skill requirements
        # Format: {items}
        self.__restricted_items = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        # Handle skill addition
        if isinstance(message.item, Skill):
            self.__skills[message.item._type_id] = message.item
        # Items which are not exceptions and which have any skill requirement
        # are tracked
        if (
            message.item._type.required_skills and
            not isinstance(message.item, EXCEPTIONS)
        ):
            self.__restricted_items.add(message.item)

    def _handle_item_removal(self, message):
        # Handle skill removal
        if isinstance(message.item, Skill):
            del self.__skills[message.item._type_id]
        # Handle restricted item removal
        self.__restricted_items.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal}

    def validate(self):
        tainted_items = {}
        # Go through restricted items
        for item in self.__restricted_items:
            # Container for skill requirement errors for current item
            skillrq_errors = []
            # Check each skill requirement
            for skillrq_type_id, skillrq_level in (
                item._type.required_skills.items()
            ):
                # Get skill level with None as fallback value for case when we
                # don't have such skill
                try:
                    skill_level = self.__skills[skillrq_type_id].level
                except KeyError:
                    skill_level = None
                # Last check - if skill level is lower than expected, current
                # item is tainted; mark it so and move to the next one
                if skill_level is None or skill_level < skillrq_level:
                    skill_requirement_error = SkillRequirementErrorData(
                        skill=skillrq_type_id,
                        level=skill_level,
                        required_level=skillrq_level)
                    skillrq_errors.append(skill_requirement_error)
            if skillrq_errors:
                tainted_items[item] = tuple(skillrq_errors)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.skill_requirement
