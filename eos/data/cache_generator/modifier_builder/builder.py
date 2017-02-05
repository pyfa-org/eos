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
from .converter import ExpressionTreeConverter, ModifierInfoConverter
from .exception import UnknownEtreeRootOperandError, YamlParsingError


logger = getLogger(__name__)


class ModifierBuilder:
    """
    Class which is used for generating Eos modifiers out of
    effect data.
    """

    def __init__(self, expressions):
        self._tree = ExpressionTreeConverter(expressions)
        self._info = ModifierInfoConverter()

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
            try:
                modifiers, build_failures = self._info.convert(effect_row)
            except YamlParsingError as e:
                effect_id = effect_row['effect_id']
                msg = 'failed to build modifiers for effect {}: {}'.format(effect_id, e.args[0])
                logger.error(msg)
                return (), EffectBuildStatus.error
        # When no modifierInfo specified, use expression trees
        # to make modifiers
        elif effect_row['pre_expression']:
            try:
                modifiers, build_failures = self._tree.convert(effect_row)
            # There're quite many root-level operands we do not
            # handle and do not want to handle. Special effects,
            # non-modifier definitions. Handle these somewhat
            # gracefully and mark such effects as skipped
            except UnknownEtreeRootOperandError as e:
                effect_id = effect_row['effect_id']
                msg = 'failed to build modifiers for effect {}: {}'.format(effect_id, e.args[0])
                logger.info(msg)
                return (), EffectBuildStatus.skipped
        # We tried and didn't find anythingto do, that's a success
        else:
            return (), EffectBuildStatus.success
        # Validate all the modifiers after building
        valid_modifiers, validation_failures = self.__get_valid_modifiers(modifiers)
        # Logging and reporting
        if build_failures == 0 and validation_failures == 0:
            return valid_modifiers, EffectBuildStatus.success
        else:
            effect_id = effect_row['effect_id']
            total_modifiers = build_failures + validation_failures + len(valid_modifiers)
            msg_segments = []
            if build_failures > 0:
                msg_segments.append('{} build errors'.format(build_failures))
            if validation_failures > 0:
                msg_segments.append('{} validation failures'.format(validation_failures))
            msg = 'effect {}, building {} modifiers: {}'.format(
                effect_id, total_modifiers, ', '.join(msg_segments))
            logger.error(msg)
            if len(valid_modifiers) > 0:
                return valid_modifiers, EffectBuildStatus.success_partial
            else:
                return (), EffectBuildStatus.error

    def __get_valid_modifiers(self, modifiers):
        valid_modifiers = []
        validation_failures = 0
        for modifier in modifiers:
            if modifier._valid is True:
                valid_modifiers.append(modifier)
            else:
                validation_failures += 1
        return valid_modifiers, validation_failures
