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


from eos.const.eos import State, Location, EffectBuildStatus, Context, FilterType, Operator
from eos.const.eve import Type, Group, Attribute, Effect, EffectCategory


class CacheCustomizer:
    """
    Run customizations on the cache. Currently only
    built-in customizations are supported, which are
    used to compensate some hardcoded data.

    Positional keywords:
    logger -- logger to use for errors
    """

    def __init__(self, logger):
        self._logger = logger

    def run_builtin(self, data):
        self.data = data
        self._add_character_missile_damage_multiplier()
        self._fix_online_effect_category()

    def _add_character_missile_damage_multiplier(self):
        """
        Some modules, like ballistic control systems, do not affect
        missile attributes directly; instead, they affect an attribute
        on the character, which, in turn, should affect missiles. The
        problem is that it doesn't affect missiles (probably some
        hardcoding on CCP's part), so we're adding it manually.
        """
        # Generate modifiers
        damage_modifiers = []
        modifier_id = max(self.data['modifiers'], key=lambda row: row['modifier_id'])['modifier_id'] + 1
        for damageAttr in (Attribute.em_damage, Attribute.thermal_damage,
                           Attribute.kinetic_damage, Attribute.explosive_damage):
            modifier_row = {
                'modifier_id': modifier_id,
                'state': State.offline,
                'context': Context.local,
                'source_attribute_id': Attribute.missile_damage_multiplier,
                'operator': Operator.post_mul,
                'target_attribute_id': damageAttr,
                'location': Location.space,
                'filter_type': FilterType.skill,
                'filter_value': Type.missile_launcher_operation
            }
            damage_modifiers.append(modifier_row)
            modifier_id += 1
        self.data['modifiers'].extend(damage_modifiers)
        # Generate effect
        effect_id = max(self.data['effects'], key=lambda row: row['effect_id'])['effect_id'] + 1
        effect_row = {
            'effect_id': effect_id,
            'effect_category': EffectCategory.passive,
            'is_offensive': False,
            'is_assistance': False,
            'duration_attribute_id': None,
            'discharge_attribute_id': None,
            'range_attribute_id': None,
            'falloff_attribute_id': None,
            'tracking_speed_attribute_id': None,
            'fitting_usage_chance_attribute_id': None,
            'build_status': EffectBuildStatus.ok_full,
            'modifiers': [modifier_row['modifier_id'] for modifier_row in damage_modifiers]
        }
        self.data['effects'].append(effect_row)
        # Add effect to all characters
        for type_row in self.data['types']:
            if type_row['group_id'] == Group.character:
                type_row['effects'].append(effect_id)

    def _fix_online_effect_category(self):
        """
        For some weird reason, 'online' effect has 'active' effect
        category, which lets all items with it to be in active state.
        CCP probably does some hardcoding to avoid it, we'll get rid
        of it on cache building time.
        """
        online_effect = None
        for effect_row in self.data['effects']:
            if effect_row['effect_id'] == Effect.online:
                online_effect = effect_row
                break
        if online_effect is None:
            msg = 'unable to find online effect'
            self._logger.warning(msg, child_name='cache_customizer')
        elif online_effect['effect_category'] == EffectCategory.online:
            msg = 'online effect category does not need to be adjusted'
            self._logger.warning(msg, child_name='cache_customizer')
        else:
            online_effect['effect_category'] = EffectCategory.online
