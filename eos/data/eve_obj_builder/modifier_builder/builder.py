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


from logging import getLogger

from eos.const.eos import EffectBuildStatus
from .converter import ExpressionTreeConverter, ModifierInfoConverter
from .exception import UnknownEtreeRootOperandError, YamlParsingError


logger = getLogger(__name__)


class ModifierBuilder:
    """Builds modifiers out of effect data.

    This class actually doesn't do much: routes tasks between two child
    converters and reports results.
    """

    def __init__(self, exp_rows):
        """Initialize builder.

        Args:
            exp_rows: Iterable with expression rows.
        """
        self._tree = ExpressionTreeConverter(exp_rows)

    def build(self, effect_row):
        """Generate modifiers using passed data.

        Args:
            effect_row: Effect row with effect category, pre-/post-expression
                IDs, modifier info data.

        Returns:
            Tuple with with iterable which contains modifiers and effect's
            modifier build status.
        """
        modinfo = effect_row.get('modifierInfo')
        pre_exp = effect_row.get('preExpression')
        # modifierInfo takes a priority
        if modinfo:
            try:
                mods, fails = ModifierInfoConverter.convert(modinfo)
            except YamlParsingError as e:
                effect_id = effect_row['effectID']
                msg = 'failed to build modifiers for effect {}: {}'.format(
                    effect_id, e.args[0])
                logger.error(msg)
                return (), EffectBuildStatus.error
        # When no modifierInfo specified, use expression trees
        elif pre_exp:
            try:
                mods, fails = self._tree.convert(pre_exp)
            # There're quite many root-level operands we do not handle and do
            # not want to handle. Special effects, non-modifier definitions.
            # Handle these somewhat gracefully and mark such effects as skipped
            except UnknownEtreeRootOperandError as e:
                effect_id = effect_row['effectID']
                msg = 'failed to build modifiers for effect {}: {}'.format(
                    effect_id, e.args[0])
                logger.info(msg)
                return (), EffectBuildStatus.skipped
        # We tried and didn't find anything to do, that's a success
        else:
            return (), EffectBuildStatus.success
        # Validate all the modifiers after building
        valid_mods, valid_fails = self.__get_valid_modifiers(mods)
        # Logging and reporting
        if fails == 0 and valid_fails == 0:
            return valid_mods, EffectBuildStatus.success
        else:
            effect_id = effect_row['effectID']
            total_mods = fails + valid_fails + len(valid_mods)
            msg_parts = []
            if fails > 0:
                msg_parts.append('{} build errors'.format(fails))
            if valid_fails > 0:
                msg_parts.append('{} validation failures'.format(valid_fails))
            msg = 'effect {}, building {} modifiers: {}'.format(
                effect_id, total_mods, ', '.join(msg_parts))
            logger.error(msg)
            if valid_mods:
                return valid_mods, EffectBuildStatus.success_partial
            else:
                return (), EffectBuildStatus.error

    def __get_valid_modifiers(self, mods):
        valid_mods = []
        valid_fails = 0
        for mod in mods:
            if mod._valid:
                valid_mods.append(mod)
            else:
                valid_fails += 1
        return valid_mods, valid_fails
