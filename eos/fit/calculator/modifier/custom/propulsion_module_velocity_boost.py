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


from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Attribute
from ..base import BaseModifier
from ..exception import ModificationCalculationError


class PropulsionModuleVelocityBoostModifier(BaseModifier):

    def __init__(self):
        BaseModifier.__init__(
            self, state=State.active, tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.ship, tgt_filter_extra_arg=None,
            tgt_attr=Attribute.max_velocity
        )

    def _get_modification(self, carrier_item, fit):
        ship_attributes = fit.ship.attributes
        carrier_attributes = carrier_item.attributes
        try:
            mass = ship_attributes[Attribute.mass]
            speed_boost = carrier_attributes[Attribute.speed_factor]
            thrust = carrier_attributes[Attribute.speed_boost_factor]
        except KeyError as e:
            raise ModificationCalculationError from e
        try:
            ship_speed_percentage = speed_boost * thrust / mass
        except ZeroDivisionError as e:
            raise ModificationCalculationError from e
        return ModifierOperator.post_percent, ship_speed_percentage
