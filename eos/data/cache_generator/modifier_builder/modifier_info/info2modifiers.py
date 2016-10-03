# ===============================================================================
# Copyright (C) 2015 Anton Vorobyov
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


import yaml
from logging import getLogger

from eos.const.eos import State, Domain, EffectBuildStatus, Scope, FilterType, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object import Modifier
from .exception import (
    UnknownStateError, UnknownOperatorError, UnknownFuncError, NoFilterValueError, UnexpectedDomainError
)


logger = getLogger(__name__)

# Format:
# {info func: (mod filter type, info attribute name for mod filter value,
#   {info domain: (mod scope, mod domain)})}
filter_map = {
    'ItemModifier': (
        None, None,
        {
            'shipID': (Scope.local, Domain.ship),
            'charID': (Scope.local, Domain.character),
            'otherID': (Scope.local, Domain.other),
            'targetID': (Scope.projected, Domain.ship),
            None: (Scope.local, Domain.self_)
        }
    ),
    'LocationModifier': (
        FilterType.all_, None,
        {
            'shipID': (Scope.local, Domain.ship),
            'charID': (Scope.local, Domain.character),
            'targetID': (Scope.projected, Domain.ship)
        }
    ),
    'LocationGroupModifier': (
        FilterType.group, 'groupID',
        {
            'shipID': (Scope.local, Domain.ship),
            'charID': (Scope.local, Domain.character),
            'targetID': (Scope.projected, Domain.ship)
        }
    ),
    'LocationRequiredSkillModifier': (
        FilterType.skill, 'skillTypeID',
        {
            'shipID': (Scope.local, Domain.ship),
            'charID': (Scope.local, Domain.character),
            'targetID': (Scope.projected, Domain.ship)
        }
    ),
    'OwnerRequiredSkillModifier': (
        FilterType.skill, 'skillTypeID',
        {
            'charID': (Scope.local, Domain.space)
        }
    ),
    'GangItemModifier': (
        None, None,
        {
            'shipID': (Scope.gang, Domain.ship),
            'charID': (Scope.gang, Domain.character)
        }
    ),
    'GangGroupModifier': (
        FilterType.group, 'groupID',
        {
            'shipID': (Scope.gang, Domain.ship),
            'charID': (Scope.gang, Domain.character)
        }
    ),
    'GangRequiredSkillModifier': (
        FilterType.skill, 'skillTypeID',
        {
            'shipID': (Scope.gang, Domain.ship),
            'charID': (Scope.gang, Domain.character)
        }
    )
}

# Format:
# {CCP operator ID: eos operator ID}
operator_map = {
    -1: Operator.pre_assign,
    0: Operator.pre_mul,
    1: Operator.pre_div,
    2: Operator.mod_add,
    3: Operator.mod_sub,
    4: Operator.post_mul,
    5: Operator.post_div,
    6: Operator.post_percent,
    7: Operator.post_assign,
}

state_map = {
    EffectCategory.passive: State.offline,
    EffectCategory.active: State.active,
    EffectCategory.target: State.active,
    EffectCategory.online: State.online,
    EffectCategory.overload: State.overload,
    EffectCategory.system: State.offline
}


class Info2Modifiers:
    """
    Parse modifierInfos into actual Modifier objects.
    """

    def convert(self, effect_row):
        """
        Parse YAML and handle overall workflow and error handling
        flow for modifier info-to-modifier conversion process.
        """
        try:
            # Assume everything goes as we want
            build_status = EffectBuildStatus.ok_full
            # Parse modifierInfo field (which is actually YAML)
            modifier_infos_yaml = effect_row['modifier_info']
            try:
                modifier_infos = yaml.safe_load(modifier_infos_yaml)
            except KeyboardInterrupt:
                raise
            except Exception:
                effect_id = effect_row['effect_id']
                msg = 'failed to parse modifier info YAML for effect {}'.format(effect_id)
                logger.error(msg)
                # We cannot recover any data in this case, thus return empty list
                return (), EffectBuildStatus.error
            # Go through modifier objects and attempt to convert them one-by-one
            modifiers = []
            for modifier_info in modifier_infos:
                modifier = Modifier()
                try:
                    self._conv_generic(modifier, modifier_info)
                    self._conv_filter(modifier, modifier_info)
                except (UnknownFuncError, NoFilterValueError, UnexpectedDomainError, UnknownOperatorError) as e:
                    effect_id = effect_row['effect_id']
                    msg = 'failed to build one of the modifiers of effect {}: {}'.format(effect_id, e.args[0])
                    logger.warning(msg)
                    # When conversion of one of modifiers failed, mark build status
                    # as partially corrupted
                    build_status = EffectBuildStatus.ok_partial
                else:
                    modifiers.append(modifier)
            # If after conversion process we have some modifiers skipped and ended up
            # with no modifiers in the list, consider whole conversion process to be
            # a failure
            if build_status == EffectBuildStatus.ok_partial and len(modifiers) == 0:
                return (), EffectBuildStatus.error
            try:
                self._conv_state(modifiers, effect_row)
            except UnknownStateError as e:
                effect_id = effect_row['effect_id']
                msg = 'failed to build modifiers for effect {}: {}'.format(effect_id, e.args[0])
                logger.warning(msg)
                # Modifiers without state data will be useless, and we cannot do any
                # safe assumptions here, , thus consider that everything went wrong
                # and return empty list
                return (), EffectBuildStatus.error
        except KeyboardInterrupt:
            raise
        except Exception:
            effect_id = effect_row['effect_id']
            msg = 'failed to build modifiers for effect {} due to unknown reason'.format(effect_id)
            logger.error(msg)
            return (), EffectBuildStatus.error
        else:
            return modifiers, build_status

    def _conv_generic(self, modifier, modifier_info):
        """
        Fill in generic modifier fields, which are stored as
        modifier info attributes.
        """
        # Operator
        info_operator = modifier_info.get('operator')
        try:
            modifier.operator = operator_map[info_operator]
        except KeyError as e:
            msg = 'unknown operator {}'.format(info_operator)
            raise UnknownOperatorError(msg) from e
        # Source attribute
        modifier.src_attr = modifier_info.get('modifyingAttributeID')
        # Target attribute
        modifier.tgt_attr = modifier_info.get('modifiedAttributeID')

    def _conv_filter(self, modifier, modifier_info):
        """
        Fill in fields which are related to filter (as in,
        which help to find object which carries attribute-
        target for modification).
        """
        # Filter type
        func_name = modifier_info['func']
        try:
            ftype, fattr, domain_data = filter_map[func_name]
        except KeyError as e:
            msg = 'unknown filter function {}'.format(func_name)
            raise UnknownFuncError(msg) from e
        if ftype is not None:
            modifier.filter_type = ftype
        # Filter value
        if fattr is not None:
            try:
                modifier.filter_value = modifier_info[fattr]
            except KeyError as e:
                msg = 'unable to find attribute {} for filter value'.format(fattr)
                raise NoFilterValueError(msg) from e
        # Scope and domain
        domain = modifier_info['domain']
        try:
            scope, domain = domain_data[domain]
        except KeyError as e:
            msg = 'unexpected domain {} for filter function {}'.format(domain, func_name)
            raise UnexpectedDomainError(msg) from e
        modifier.scope = scope
        modifier.domain = domain

    def _conv_state(self, modifiers, effect_row):
        """
        State is stored on effect object, thus run separate
        cycle for all modifiers we generated.
        """
        effect_category = effect_row['effect_category']
        try:
            state = state_map[effect_category]
        except KeyError as e:
            msg = 'cannot convert effect category {} into state'.format(effect_category)
            raise UnknownStateError(msg) from e
        for modifier in modifiers:
            modifier.state = state
