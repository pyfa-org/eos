# ===============================================================================
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
# ===============================================================================


from logging import getLogger

from eos.const.eos import EffectBuildStatus
from .expression_tree import ExpressionTree2Modifiers
from .modifier_info import ModifierInfo2Modifiers


logger = getLogger(__name__)


class ModifierBuilder:
    """
    Class which is used for generating Eos modifiers out of
    effect data.
    """

    def __init__(self, expressions):
        self._tree = ExpressionTree2Modifiers(expressions)
        self._info = ModifierInfo2Modifiers()

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
            modifiers, build_status, build_failures = self._info.convert(effect_row)
        # When no modifierInfo specified, use expression trees
        # to make modifiers
        elif effect_row['pre_expression']:
            modifiers, build_status, build_failures = self._tree.convert(effect_row)
        else:
            return (), EffectBuildStatus.success
        # Validate all the modifiers after building
        valid_modifiers = []
        validation_failures = 0
        for modifier in modifiers:
            if modifier._valid is True:
                valid_modifiers.append(modifier)
            else:
                validation_failures += 1
        # Logging
        if build_failures > 0:
            effect_id = effect_row['effect_id']
            total_modifiers = build_failures + validation_failures + len(valid_modifiers)
            logger.error('failed to build {}/{} modifiers of effect {}'.format(
                build_failures, total_modifiers, effect_id))
        if validation_failures > 0:
            effect_id = effect_row['effect_id']
            total_modifiers = build_failures + validation_failures + len(valid_modifiers)
            logger.error('{}/{} modifiers of effect {} failed validation'.format(
                validation_failures, total_modifiers, effect_id))
        # Do not modify effect build status if there're no errors, to keep
        # YAML parsing errors and skipped expression tree effect statuses
        if build_failures == 0 and validation_failures == 0:
            return valid_modifiers, build_status
        else:
            if len(valid_modifiers) > 0:
                return valid_modifiers, EffectBuildStatus.success_partial
            else:
                return (), EffectBuildStatus.error
