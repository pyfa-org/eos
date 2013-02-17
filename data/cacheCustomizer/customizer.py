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


from eos.const import State, Location, EffectBuildStatus, Context, FilterType, Operator
from eos.eve.const import Type, Group, Attribute, EffectCategory


class CacheCustomizer:
    """
    Run customizations on the cache. Currently only
    built-in customizations are supported, which are
    used to compensate some hardcoded data.
    """

    def runBuiltIn(self, data):
        self.data = data
        self._addCharacterMissileDamageMultiplier()

    def _addCharacterMissileDamageMultiplier(self):
        """
        Some modules, like ballistic control systems, do not affect
        missile attributes firectly; instead, they affect attribute
        on character, which, in turn, should affect missiles. The
        problem is that it doesn't affect missiles (probably some
        hardcoding on CCP's part), so we're adding it manually.
        """
        # Generate modifiers
        damageModifiers = []
        modifierId = max(self.data['modifiers'], key=lambda row: row['modifierId'])['modifierId'] + 1
        for damageAttr in (Attribute.emDamage, Attribute.thermalDamage,
                           Attribute.kineticDamage, Attribute.explosiveDamage):
            modifierRow = {'modifierId': modifierId,
                           'state': State.offline,
                           'context': Context.local,
                           'sourceAttributeId': Attribute.missileDamageMultiplier,
                           'operator': Operator.postMul,
                           'targetAttributeId': damageAttr,
                           'location': Location.space,
                           'filterType': FilterType.skill,
                           'filterValue': Type.missileLauncherOperation}
            damageModifiers.append(modifierRow)
            modifierId += 1
        self.data['modifiers'].extend(damageModifiers)
        # Generate effect
        effectId = max(self.data['effects'], key=lambda row: row['effectId'])['effectId'] + 1
        effectRow = {'effectId': effectId,
                     'effectCategory': EffectCategory.passive,
                     'isOffensive': False,
                     'isAssistance': False,
                     'fittingUsageChanceAttributeId': None,
                     'buildStatus': EffectBuildStatus.okFull,
                     'modifiers': [modifierRow['modifierId'] for modifierRow in damageModifiers]}
        self.data['effects'].append(effectRow)
        # Add effect to all characters
        for typeRow in self.data['types']:
            if typeRow['groupId'] == Group.character:
                typeRow['effects'].append(effectId)
