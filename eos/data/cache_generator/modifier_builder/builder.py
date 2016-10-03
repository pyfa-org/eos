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


from .expression_tree import Effect2Modifiers
from .modifier_info import Info2Modifiers


class ModifierBuilder:
    """
    Class which is used for generating Eos modifiers out of
    effect data.
    """

    def __init__(self, expressions):
        self._tree = Effect2Modifiers(expressions)
        self._info = Info2Modifiers()

    def build(self, effect_row):
        """
        Generate modifiers using passed data.

        Required arguments:
        effect_row -- effect row with effect category, pre-/post-
        expression ID, modifier info data.

        Return value:
        Tuple with list of modifiers and effect build status
        """
        if effect_row['modifier_info']:
            modifiers, build_status = self._info.convert(effect_row)
        # When no modifierInfo specified, use expression trees
        # to make modifiers
        else:
            modifiers, build_status = self._tree.convert(effect_row)
        return modifiers, build_status
