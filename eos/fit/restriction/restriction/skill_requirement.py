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
from eos.fit.item import Rig
from eos.fit.item import Skill
from eos.fit.message import ItemLoaded
from eos.fit.message import ItemUnloaded
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


SkillRequirementErrorData = namedtuple(
    'SkillRequirementErrorData', ('skill_type_id', 'level', 'required_level'))

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

    def __init__(self, fit):
        self.__fit = fit
        # Set with items which have any skill requirements
        # Format: {items}
        self.__restricted_items = set()
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_loaded(self, msg):
        if (
            msg.item._type.required_skills and
            not isinstance(msg.item, EXCEPTIONS)
        ):
            self.__restricted_items.add(msg.item)

    def _handle_item_unloaded(self, msg):
        self.__restricted_items.discard(msg.item)

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}

    def validate(self):
        tainted_items = {}
        skills = self.__fit.skills
        # Go through restricted items
        for item in self.__restricted_items:
            # Container for skill requirement errors for current item
            skillrq_errors = []
            # Check each skill requirement
            for skillrq_type_id, skillrq_level in (
                item._type.required_skills.items()
            ):
                # Get skill level with None as fallback value for case when we
                # don't have such skill or it's not loaded
                try:
                    skill = skills[skillrq_type_id]
                except KeyError:
                    skill_level = None
                else:
                    if skill._is_loaded:
                        skill_level = skill.level
                    else:
                        skill_level = None
                # Last check - if skill level is lower than expected, current
                # item is tainted; mark it so and move to the next one
                if skill_level is None or skill_level < skillrq_level:
                    skill_requirement_error = SkillRequirementErrorData(
                        skill_type_id=skillrq_type_id,
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
