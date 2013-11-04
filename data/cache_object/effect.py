#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


class Effect:
    """
    Represents a single effect. Effects are the building blocks which describe what its carrier
    does with other items.
    """

    def __init__(self,
                 effect_id=None,
                 category_id=None,
                 is_offensive=None,
                 is_assistance=None,
                 fitting_usage_chance_attribute_id=None,
                 build_status=None,
                 modifiers=()):
        self.id = effect_id

        # Effect category actually describes type of effect, which determines
        # when it is applied - always, when item is active, overloaded, etc.
        self.category_id = category_id

        # Whether the effect is offensive (e.g. guns)
        self.is_offensive = bool(is_offensive) if is_offensive is not None else None

        # Whether the effect is helpful (e.g. remote repairers)
        self.is_assistance = bool(is_assistance) if is_assistance is not None else None

        # Refers attribute, which determines chance of effect
        # getting applied when its carrier is added to fit
        self.fitting_usage_chance_attribute_id = fitting_usage_chance_attribute_id

        # Stores expression->modifiers parsing status
        self.build_status = build_status

        # Stores Modifiers which are assigned to given effect
        self.modifiers = modifiers
