# ==============================================================================
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
# ==============================================================================


from logging import getLogger

from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import AttributeId
from eos.fit.message import AttrValueChanged
from ...modifier.exception import ModificationCalculationError
from ...modifier.python import BasePythonModifier


logger = getLogger(__name__)


class PropulsionModuleVelocityBoostModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self, tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.ship, tgt_filter_extra_arg=None,
            tgt_attr_id=AttributeId.max_velocity)

    def get_modification(self, carrier_item, ship):
        # If attribute values of any necessary items are not available, do not
        # calculate anything
        try:
            mass = ship.attributes[AttributeId.mass]
            speed_boost = carrier_item.attributes[AttributeId.speed_factor]
            thrust = carrier_item.attributes[AttributeId.speed_boost_factor]
        except (AttributeError, KeyError) as e:
            raise ModificationCalculationError from e
        try:
            ship_speed_percentage = speed_boost * thrust / mass
        # Log warning for zero ship mass, as it's abnormal situation
        except ZeroDivisionError as e:
            msg = (
                'cannot calculate propulsion speed boost due to zero ship mass')
            logger.warning(msg)
            raise ModificationCalculationError from e
        return ModifierOperator.post_percent, ship_speed_percentage

    def __revise_on_attr_changed(self, message, carrier_item, ship):
        """
        If any of the attribute values this modifier relies on is changed,
        then modification value can be changed as well.
        """
        if (
            (message.item is ship and message.attr == AttributeId.mass) or
            (
                message.item is carrier_item and
                message.attr == AttributeId.speed_factor
            ) or (
                message.item is carrier_item and
                message.attr == AttributeId.speed_boost_factor
            )
        ):
            return True
        return False

    __revision_map = {
        AttrValueChanged: __revise_on_attr_changed}

    @property
    def revise_message_types(self):
        return set(self.__revision_map)

    def revise_modification(self, message, carrier_item, ship):
        revision_func = self.__revision_map[type(message)]
        return revision_func(self, message, carrier_item, ship)
