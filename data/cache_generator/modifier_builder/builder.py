#===============================================================================
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
#===============================================================================


from .expression_tree import Effect2Modifiers


class ModifierBuilder:
    """
    Class which is used for generating Eos modifiers out of
    effect data.
    """

    def __init__(self, expressions, logger):
        self._tree = Effect2Modifiers(expressions, logger)


    def build(self, effect_row):
        modifiers, build_status = self._tree.convert(
            effect_row['pre_expression_id'],
            effect_row['post_expression_id'],
            effect_row['effect_category']
        )
        return modifiers, build_status
