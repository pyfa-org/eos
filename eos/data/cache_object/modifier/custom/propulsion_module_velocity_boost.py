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
from eos.fit.messages import AttrValueChanged, AttrValueChangedOverride
from ..python import BasePythonModifier
from ..exception import ModificationCalculationError


class PropulsionModuleVelocityBoostModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self, state=State.active, tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.ship, tgt_filter_extra_arg=None,
            tgt_attr=Attribute.max_velocity
        )

    def get_modification(self, carrier_item, fit):
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

    def _revise_on_attr_change(self, message, carrier_item, fit):
        """
        If any of the attribute values this modifier relies on is changed,
        then modification value can be changed as well.
        """
        if (
            (message.item is fit.ship and message.attr == Attribute.mass) or
            (message.item is carrier_item and message.attr == Attribute.speed_factor) or
            (message.item is carrier_item and message.attr == Attribute.speed_boost_factor)
        ):
            return True
        return False

    _revision_map = {
        AttrValueChanged: _revise_on_attr_change,
        AttrValueChangedOverride: _revise_on_attr_change
    }

    @property
    def revise_message_types(self):
        return set(self._revision_map.keys())

    def revise_modification(self, message, carrier_item, fit):
        revision_func = self._revision_map[type(message)]
        return revision_func(self, message, carrier_item, fit)
