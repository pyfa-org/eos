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


from eos.const.eos import ModAggregateMode
from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModOperator
from eos.eve_obj.buff_template import WarfareBuffTemplate


class WarfareBuffTemplateBuilder:

    @classmethod
    def build(cls, buff_row):
        buff_templates = []
        for mod_row in buff_row.get('itemModifiers', ()):
            buff_templates.append(
                cls._handle_item_mod(buff_row, mod_row))
        for mod_row in buff_row.get('locationModifiers', ()):
            buff_templates.append(
                cls._handle_domain_mod(buff_row, mod_row))
        for mod_row in buff_row.get('locationGroupModifiers', ()):
            buff_templates.append(
                cls._handle_domain_group_mod(buff_row, mod_row))
        for mod_row in buff_row.get('locationRequiredSkillModifiers', ()):
            buff_templates.append(
                cls._handle_domain_skillrq_mod(buff_row, mod_row))
        return buff_templates

    @classmethod
    def _handle_item_mod(cls, buff_row, mod_row):
        return WarfareBuffTemplate(
            buff_id=buff_row['buffID'],
            affectee_filter=ModAffecteeFilter.item,
            affectee_attr_id=mod_row['dogmaAttributeID'],
            operator=cls._get_operator(buff_row),
            aggregate_mode=cls._get_aggregate_mode(buff_row))

    @classmethod
    def _handle_domain_mod(cls, buff_row, mod_row):
        return WarfareBuffTemplate(
            buff_id=buff_row['buffID'],
            affectee_filter=ModAffecteeFilter.domain,
            affectee_attr_id=mod_row['dogmaAttributeID'],
            operator=cls._get_operator(buff_row),
            aggregate_mode=cls._get_aggregate_mode(buff_row))

    @classmethod
    def _handle_domain_group_mod(cls, buff_row, mod_row):
        return WarfareBuffTemplate(
            buff_id=buff_row['buffID'],
            affectee_filter=ModAffecteeFilter.domain_group,
            affectee_filter_extra_arg=mod_row['groupID'],
            affectee_attr_id=mod_row['dogmaAttributeID'],
            operator=cls._get_operator(buff_row),
            aggregate_mode=cls._get_aggregate_mode(buff_row))

    @classmethod
    def _handle_domain_skillrq_mod(cls, buff_row, mod_row):
        return WarfareBuffTemplate(
            buff_id=buff_row['buffID'],
            affectee_filter=ModAffecteeFilter.domain_skillrq,
            affectee_filter_extra_arg=mod_row['skillID'],
            affectee_attr_id=mod_row['dogmaAttributeID'],
            operator=cls._get_operator(buff_row),
            aggregate_mode=cls._get_aggregate_mode(buff_row))

    @staticmethod
    def _get_operator(buff_row):
        # Format: {buff operator name: eos operator ID}
        conversion_map = {
            'PreAssignment': ModOperator.pre_assign,
            'PreMul': ModOperator.pre_mul,
            'PreDiv': ModOperator.pre_div,
            'ModAdd': ModOperator.mod_add,
            'ModSub': ModOperator.mod_sub,
            'PostMul': ModOperator.post_mul,
            'PostDiv': ModOperator.post_div,
            'PostPercent': ModOperator.post_percent,
            'PostAssignment': ModOperator.post_assign}
        return conversion_map[buff_row['operationName']]

    @staticmethod
    def _get_aggregate_mode(buff_row):
        # Format: {buff aggregate mode name: eos aggregate mode ID}
        conversion_map = {
            'Minimum': ModAggregateMode.minimum,
            'Maximum': ModAggregateMode.maximum}
        return conversion_map[buff_row['aggregateMode']]
