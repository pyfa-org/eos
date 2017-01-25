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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


ChargeSizeErrorData = namedtuple('ChargeSizeErrorData', ('holder_size', 'allowed_size'))


class ChargeSizeRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    If holder can fit charges and specifies size of charges it
    can fit, other sizes cannot be loaded into it.

    Details:
    If container specifies size and holder doesn't specify it,
        charge is not allowed to be loaded.
    If container does not specify size, charge of any size
        can be loaded.
    To determine allowed size and charge size, EVE type attributes
        are used.
    """

    def __init__(self):
        self.__restricted_containers = set()

    def register_item(self, holder):
        # Ignore container holders without charge attribute
        if not hasattr(holder, 'charge'):
            return
        # And without size specification
        if Attribute.charge_size not in holder._eve_type.attributes:
            return
        self.__restricted_containers.add(holder)

    def unregister_item(self, holder):
        self.__restricted_containers.discard(holder)

    def validate(self):
        tainted_holders = {}
        # Go through containers with charges, and if their
        # sizes mismatch - taint charge holders
        for container in self.__restricted_containers:
            charge = container.charge
            if charge is None:
                continue
            container_size = container._eve_type.attributes[Attribute.charge_size]
            charge_size = charge._eve_type.attributes.get(Attribute.charge_size)
            if container_size != charge_size:
                tainted_holders[charge] = ChargeSizeErrorData(
                    holder_size=charge_size,
                    allowed_size=container_size
                )
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.charge_size
