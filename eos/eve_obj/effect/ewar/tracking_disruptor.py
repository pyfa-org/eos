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


from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModAggregateMode
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.const.eve import TypeId
from eos.eve_obj.effect import Effect
from eos.eve_obj.effect import EffectFactory
from eos.eve_obj.modifier import DogmaModifier


class ShipModuleTrackingDisruptor(Effect):

    def __init__(self, *args, **kwargs):
        Effect.__init__(self, *args, **kwargs)
        max_range_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.domain_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.gunnery,
            affectee_attr_id=AttrId.max_range,
            operator=ModOperator.post_percent,
            aggregate_mode=ModAggregateMode.stack,
            affector_attr_id=AttrId.max_range_bonus)
        falloff_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.domain_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.gunnery,
            affectee_attr_id=AttrId.falloff,
            operator=ModOperator.post_percent,
            aggregate_mode=ModAggregateMode.stack,
            affector_attr_id=AttrId.falloff_bonus)
        tracking_speed_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.domain_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.gunnery,
            affectee_attr_id=AttrId.tracking_speed,
            operator=ModOperator.post_percent,
            aggregate_mode=ModAggregateMode.stack,
            affector_attr_id=AttrId.tracking_speed_bonus)
        self.modifiers = (
            *self.modifiers, max_range_modifier,
            falloff_modifier, tracking_speed_modifier)


EffectFactory.register_class_by_id(
    ShipModuleTrackingDisruptor,
    EffectId.ship_module_tracking_disruptor)
