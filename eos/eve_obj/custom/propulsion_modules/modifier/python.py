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


from logging import getLogger

from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModAggregateMode
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eve import AttrId
from eos.eve_obj.modifier import BasePythonModifier
from eos.eve_obj.modifier import ModificationCalculationError
from eos.pubsub.message import AttrsValueChanged


logger = getLogger(__name__)


class PropulsionModuleVelocityBoostModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self,
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.ship,
            affectee_filter_extra_arg=None,
            affectee_attr_id=AttrId.max_velocity)

    def get_modification(self, affector_item):
        ship = affector_item._fit.ship
        # If attribute values of any necessary items are not available, do not
        # calculate anything
        try:
            mass = ship.attrs[AttrId.mass]
            speed_boost = affector_item.attrs[AttrId.speed_factor]
            thrust = affector_item.attrs[AttrId.speed_boost_factor]
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
            return ModOperator.post_mul, mult, ModAggregateMode.stack, None

    def __revise_on_attr_changed(self, msg, affector_item):
        """
        If any of the attribute values this modifier relies on is changed, then
        modification value can be changed as well.
        """
        ship = affector_item._fit.ship
        if ship in msg.attr_changes and AttrId.mass in msg.attr_changes[ship]:
            return True
        if (
            affector_item in msg.attr_changes and
                msg.attr_changes[affector_item].intersection(
                (AttrId.speed_factor, AttrId.speed_boost_factor))
        ):
            return True
        return False

    __revision_map = {
        AttrsValueChanged: __revise_on_attr_changed}

    @property
    def revise_msg_types(self):
        return set(self.__revision_map)

    def revise_modification(self, msg, affector_item):
        revision_func = self.__revision_map[type(msg)]
        return revision_func(self, msg, affector_item)
