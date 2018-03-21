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

from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.eve_object.modifier import BasePythonModifier
from eos.eve_object.modifier import ModificationCalculationError
from eos.fit.message import AttrValueChanged


logger = getLogger(__name__)


class PropulsionModuleVelocityBoostModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self, tgt_filter=ModTgtFilter.item, tgt_domain=ModDomain.ship,
            tgt_filter_extra_arg=None, tgt_attr_id=AttrId.max_velocity)

    def get_modification(self, carrier_item):
        ship = carrier_item._fit.ship
        # If attribute values of any necessary items are not available, do not
        # calculate anything
        try:
            mass = ship.attrs[AttrId.mass]
            speed_boost = carrier_item.attrs[AttrId.speed_factor]
            thrust = carrier_item.attrs[AttrId.speed_boost_factor]
        except (AttributeError, KeyError) as e:
            raise ModificationCalculationError from e
        try:
            perc = speed_boost * thrust / mass
        # Log warning for zero ship mass, as it's abnormal situation
        except ZeroDivisionError as e:
            msg = (
                'cannot calculate propulsion speed boost due to zero ship mass')
            logger.warning(msg)
            raise ModificationCalculationError from e
        else:
            mult = 1 + perc / 100
            return ModOperator.post_mul, mult

    def __revise_on_attr_changed(self, msg, carrier_item):
        """
        If any of the attribute values this modifier relies on is changed, then
        modification value can be changed as well.
        """
        ship = carrier_item._fit.ship
        if msg.item is ship and msg.attr_id == AttrId.mass:
            return True
        if (
            msg.item is carrier_item and
            msg.attr_id == AttrId.speed_factor
        ):
            return True
        if (
            msg.item is carrier_item and
            msg.attr_id == AttrId.speed_boost_factor
        ):
            return True
        return False

    __revision_map = {
        AttrValueChanged: __revise_on_attr_changed}

    @property
    def revise_msg_types(self):
        return set(self.__revision_map)

    def revise_modification(self, msg, carrier_item):
        revision_func = self.__revision_map[type(msg)]
        return revision_func(self, msg, carrier_item)
