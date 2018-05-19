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
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.const.eve import TypeId
from eos.eve_obj.effect import Effect
from eos.eve_obj.effect import EffectFactory
from eos.eve_obj.modifier import DogmaModifier


class ShipModuleGundanceDisruptor(Effect):

    def __init__(self, *args, **kwargs):
        Effect.__init__(self, *args, **kwargs)
        aoe_cloud_size_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.owner_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.missile_launcher_operation,
            affectee_attr_id=AttrId.aoe_cloud_size,
            operator=ModOperator.post_percent,
            affector_attr_id=AttrId.aoe_cloud_size_bonus)
        aoe_velocity_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.owner_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.missile_launcher_operation,
            affectee_attr_id=AttrId.aoe_velocity,
            operator=ModOperator.post_percent,
            affector_attr_id=AttrId.aoe_velocity_bonus)
        max_velocity_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.owner_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.missile_launcher_operation,
            affectee_attr_id=AttrId.max_velocity,
            operator=ModOperator.post_percent,
            affector_attr_id=AttrId.missile_velocity_bonus)
        explosion_delay_modifier = DogmaModifier(
            affectee_filter=ModAffecteeFilter.owner_skillrq,
            affectee_domain=ModDomain.target,
            affectee_filter_extra_arg=TypeId.missile_launcher_operation,
            affectee_attr_id=AttrId.explosion_delay,
            operator=ModOperator.post_percent,
            affector_attr_id=AttrId.explosion_delay_bonus)
        self.modifiers = (
            *self.modifiers, aoe_cloud_size_modifier,
            aoe_velocity_modifier, max_velocity_modifier,
            explosion_delay_modifier)


EffectFactory.reg_cust_class_by_id(
    ShipModuleGundanceDisruptor,
    EffectId.ship_module_guidance_disruptor)
