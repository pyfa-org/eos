# ==============================================================================
# Copyright (C) 2017 Anton Vorobyov
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


import yaml

from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.eve_obj.modifier import DogmaModifier
from eos.eve_obj_builder.mod_builder.exception import YamlParsingError


class ModInfoconverter:
    """Parses modifierInfos into modifiers."""

    @classmethod
    def convert(cls, mod_infos_yaml):
        """Generate modifiers out of YAML data.

        Args:
            mod_infos_yaml: String with YAML modifier data.

        Returns:
            Tuple with iterable which contains modifiers, and quantity of
            modifier build failures we recorded.

        Raises:
            YamlParsingError: If YAML parses fails.
        """
        try:
            mod_infos = yaml.safe_load(mod_infos_yaml)
        except KeyboardInterrupt:
            raise
        # We cannot recover any data in case of YAML parsing failure
        except Exception as e:
            raise YamlParsingError('failed to parse YAML') from e
        mods = []
        fails = 0
        # Get handler according to function specified in info
        for mod_info in mod_infos:
            try:
                mod_func = mod_info['func']
            except (KeyError, TypeError):
                fails += 1
                continue
            handler_map = {
                'ItemModifier': cls._handle_item_mod,
                'LocationModifier': cls._handle_domain_mod,
                'LocationGroupModifier': cls._handle_domain_group_mod,
                'LocationRequiredSkillModifier': cls._handle_domain_skillrq_mod,
                'OwnerRequiredSkillModifier': cls._handle_owner_skillrq_mod}
            # Compose and verify modifier, record if we failed to do so
            try:
                handler = handler_map[mod_func]
            except KeyError:
                fails += 1
            else:
                try:
                    mod = handler(mod_info)
                except KeyboardInterrupt:
                    raise
                except Exception:
                    fails += 1
                else:
                    mods.append(mod)
        return mods, fails

    @classmethod
    def _handle_item_mod(cls, mod_info):
        return DogmaModifier(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=cls._get_domain(mod_info),
            tgt_attr_id=int(mod_info['modifiedAttributeID']),
            operator=cls._get_operator(mod_info),
            src_attr_id=int(mod_info['modifyingAttributeID']))

    @classmethod
    def _handle_domain_mod(cls, mod_info):
        return DogmaModifier(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=cls._get_domain(mod_info),
            tgt_attr_id=int(mod_info['modifiedAttributeID']),
            operator=cls._get_operator(mod_info),
            src_attr_id=int(mod_info['modifyingAttributeID']))

    @classmethod
    def _handle_domain_group_mod(cls, mod_info):
        return DogmaModifier(
            tgt_filter=ModTgtFilter.domain_group,
            tgt_domain=cls._get_domain(mod_info),
            tgt_filter_extra_arg=int(mod_info['groupID']),
            tgt_attr_id=int(mod_info['modifiedAttributeID']),
            operator=cls._get_operator(mod_info),
            src_attr_id=int(mod_info['modifyingAttributeID']))

    @classmethod
    def _handle_domain_skillrq_mod(cls, mod_info):
        return DogmaModifier(
            tgt_filter=ModTgtFilter.domain_skillrq,
            tgt_domain=cls._get_domain(mod_info),
            tgt_filter_extra_arg=int(mod_info['skillTypeID']),
            tgt_attr_id=int(mod_info['modifiedAttributeID']),
            operator=cls._get_operator(mod_info),
            src_attr_id=int(mod_info['modifyingAttributeID']))

    @classmethod
    def _handle_owner_skillrq_mod(cls, mod_info):
        return DogmaModifier(
            tgt_filter=ModTgtFilter.owner_skillrq,
            tgt_domain=cls._get_domain(mod_info),
            tgt_filter_extra_arg=int(mod_info['skillTypeID']),
            tgt_attr_id=int(mod_info['modifiedAttributeID']),
            operator=cls._get_operator(mod_info),
            src_attr_id=int(mod_info['modifyingAttributeID']))

    @staticmethod
    def _get_domain(mod_info):
        conversion_map = {
            None: ModDomain.self,
            'itemID': ModDomain.self,
            'charID': ModDomain.character,
            'shipID': ModDomain.ship,
            'targetID': ModDomain.target,
            'otherID': ModDomain.other}
        return conversion_map[mod_info['domain']]

    @staticmethod
    def _get_operator(mod_info):
        # Format: {CCP YAML operator ID: eos operator ID}
        conversion_map = {
            -1: ModOperator.pre_assign,
            0: ModOperator.pre_mul,
            1: ModOperator.pre_div,
            2: ModOperator.mod_add,
            3: ModOperator.mod_sub,
            4: ModOperator.post_mul,
            5: ModOperator.post_div,
            6: ModOperator.post_percent,
            7: ModOperator.post_assign}
        return conversion_map[mod_info['operator']]
