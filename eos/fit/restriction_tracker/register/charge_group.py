# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


RESTRICTION_ATTRS = (
    Attribute.charge_group_1,
    Attribute.charge_group_2,
    Attribute.charge_group_3,
    Attribute.charge_group_4,
    Attribute.charge_group_5
)


ChargeGroupErrorData = namedtuple('ChargeGroupErrorData', ('holder_group', 'allowed_groups'))


class ChargeGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    If holder can fit charges and specifies group of charges it
    can fit, other groups cannot be loaded into it.

    Details:
    For validation, original values of allowed charge group
    attributes are taken.
    """

    def __init__(self):
        # Format: {container holder: (allowed groups)}
        self.__restricted_containers = {}

    def register_holder(self, holder):
        # We're going to track containers, not charges;
        # ignore all holders which can't fit a charge
        if not hasattr(holder, 'charge'):
            return
        # Compose set of charge groups this container
        # is able to fit
        allowed_groups = set()
        for restriction_attr in RESTRICTION_ATTRS:
            allowed_groups.add(holder.item.attributes.get(restriction_attr))
        allowed_groups.discard(None)
        # Only if groups were specified, consider
        # restriction enabled
        if allowed_groups:
            self.__restricted_containers[holder] = tuple(allowed_groups)

    def unregister_holder(self, holder):
        if holder in self.__restricted_containers:
            del self.__restricted_containers[holder]

    def validate(self):
        tainted_holders = {}
        # If holder has charge and its group is not allowed,
        # taint charge (not container) holder
        for container, allowed_groups in self.__restricted_containers.items():
            charge = container.charge
            if charge is None:
                continue
            if charge.item.group not in allowed_groups:
                tainted_holders[charge] = ChargeGroupErrorData(
                    holder_group=charge.item.group,
                    allowed_groups=allowed_groups
                )
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.charge_group
