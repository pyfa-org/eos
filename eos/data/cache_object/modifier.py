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


class Modifier:
    """
    Modifier objects are Eos-specific abstraction, they replace effects'
    expressions. Each modifier object contains full description of
    modification: when it should be applied, on which items, how to
    apply it, and so on.
    """

    def __init__(
        self,
        modifier_id=None,
        state=None,
        scope=None,
        src_attr=None,
        operator=None,
        tgt_attr=None,
        domain=None,
        filter_type=None,
        filter_value=None
    ):
        # Identifier of modifier, synthesized at
        # cache generation time
        self.id = modifier_id

        # Modifier can be applied only when its carrier holder
        # is in this or greater state, must be const_eos.State
        # class' attribute value.
        self.state = state

        # Describes scope in which modifier is applied, must
        # be const_eos.Scope class' attribute value.
        self.scope = scope

        # Which attribute will be taken as source value,
        # must be integer which refers attribute via ID.
        self.src_attr = src_attr

        # Which operation should be applied during modification,
        # must be const_eos.Operator class' attribute value.
        self.operator = operator

        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.tgt_attr = tgt_attr

        # Target domain to change, must be const_eos.Domain
        # class' attribute value.
        self.domain = domain

        # Filter type of the modification, must be None or
        # const_eos.FilterType class' attribute value.
        self.filter_type = filter_type

        # Filter value of the modification:
        # For filter_type.all_, filter_type.None or filter_type.skill_self must be None;
        # For filter_type.group must be some integer, referring group via ID;
        # For filter_type.skill must be some integer, referring type via ID
        self.filter_value = filter_value
