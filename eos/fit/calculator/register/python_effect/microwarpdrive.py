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


from eos.const.eos import ModifierTargetFilter, ModifierDomain, State, ModifierOperator
from eos.const.eve import Attribute, Effect
from eos.data.cache_object import Modifier
from eos.fit.messages import AttrValueChanged, AttrValueChangedOverride
from .custom_effect import CustomEffect


mass_modifier = Modifier(
    tgt_filter=ModifierTargetFilter.item,
    tgt_domain=ModifierDomain.ship,
    state=State.active,
    src_attr=Attribute.mass_addition,
    operator=ModifierOperator.mod_add,
    tgt_attr=Attribute.mass
)

signature_modifier = Modifier(
    tgt_filter=ModifierTargetFilter.item,
    tgt_domain=ModifierDomain.ship,
    state=State.active,
    src_attr=Attribute.signature_radius_bonus,
    operator=ModifierOperator.post_percent,
    tgt_attr=Attribute.signature_radius
)


class ShipSpeedModifier:

    subscriptions = (AttrValueChanged, AttrValueChangedOverride)

    @staticmethod
    def run_conditions(carrier_item, fit, message):
        if (
            (message.source_item is fit.ship and message.attr == Attribute.mass) or
            (message.source_item is carrier_item and message.attr == Attribute.speed_factor) or
            (message.source_item is carrier_item and message.attr == Attribute.speed_boost_factor)
        ):
            return True
        return False

    @staticmethod
    def run(carrier_item, fit):
        mass = fit.ship.attributes[Attribute.mass]
        speed_boost = carrier_item.attributes[Attribute.speed_factor]
        thrust = carrier_item.attributes[Attribute.speed_boost_factor]
        ship_speed_percentage = speed_boost * thrust / mass
        return ((Attribute.max_velocity, ModifierOperator.post_percent, ship_speed_percentage),)

    @staticmethod
    def target_filter(target_item, fit):
        if target_item is fit.ship:
            return True
        return False


MicroWarpDriveEffect = CustomEffect(
    effect_id=Effect.module_bonus_microwarpdrive,
    dogma_modifiers=(mass_modifier, signature_modifier),
    python_modifiers=(ShipSpeedModifier,)
)
