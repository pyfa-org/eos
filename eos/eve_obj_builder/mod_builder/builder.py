# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
from .converter import ModInfoconverter
from .exception import YamlParsingError


logger = getLogger(__name__)


class ModBuilder:
    """Builds modifiers out of effect data.

    This class actually doesn't do much: routes tasks between two child
    converters and reports results.
    """

    def build(self, effect_row):
        """Generate modifiers using passed data.

        Args:
            effect_row: Effect row with effect category and modifier info data.

        Returns:
            Tuple with with iterable which contains modifiers and effect's
            modifier build status.
        """
        mod_info = effect_row.get('modifierInfo')
        # Modifier info has priority
        if mod_info:
            try:
                mods, fails = ModInfoconverter.convert(mod_info)
            except YamlParsingError as e:
                effect_id = effect_row['effectID']
                msg = 'failed to build modifiers for effect {}: {}'.format(
                    effect_id, e.args[0])
                logger.error(msg)
                return (), EffectBuildStatus.error
        # We tried and didn't find anything to do, that's a success
        else:
            return (), EffectBuildStatus.success
        # Validate all the modifiers after building
        valid_mods, valid_fails = self.__get_valid_mods(mods)
        # Logging and reporting
        if not fails and not valid_fails:
            return valid_mods, EffectBuildStatus.success
        else:
            effect_id = effect_row['effectID']
            total_mods = fails + valid_fails + len(valid_mods)
            msg_parts = []
            if fails:
                msg_parts.append('{} build errors'.format(fails))
            if valid_fails:
                msg_parts.append('{} validation failures'.format(valid_fails))
            msg = 'effect {}, building {} modifiers: {}'.format(
                effect_id, total_mods, ', '.join(msg_parts))
            logger.error(msg)
            if valid_mods:
                return valid_mods, EffectBuildStatus.success_partial
            else:
                return (), EffectBuildStatus.error

    @staticmethod
    def __get_valid_mods(mods):
        valid_mods = []
        valid_fails = 0
        for mod in mods:
            if mod._valid:
                valid_mods.append(mod)
            else:
                valid_fails += 1
        return valid_mods, valid_fails
