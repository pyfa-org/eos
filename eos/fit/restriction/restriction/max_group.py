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

from eos.const.eos import State, Restriction
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, ModuleMed, ModuleLow
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove, InstrStatesActivate, InstrStatesDeactivate
from eos.util.keyed_set import KeyedSet
from .base import BaseRestriction
from ..exception import RestrictionValidationError


TRACKED_ITEM_CLASSES = (ModuleHigh, ModuleMed, ModuleLow)


MaxGroupErrorData = namedtuple('MaxGroupErrorData', ('item_group', 'max_group', 'group_items'))


class MaxGroupRestriction(BaseRestriction):
    """
    Class which implements common functionality for all
    registers, which track maximum number of modules in
    certain state on per-group basis.
    """

    def __init__(self, max_group_attr, restriction_type):
        # Attribute ID whose value contains group restriction of item
        self.__max_group_attr = max_group_attr
        self.__restriction_type = restriction_type
        # Container for all tracked items, keyed by their group ID
        # Format: {group ID: {items}}
        self.__group_all = KeyedSet()
        # Container for items, which have max group restriction
        # to become operational
        # Format: {items}
        self.__group_restricted = set()

    def _register_item(self, item):
        if not isinstance(item, TRACKED_ITEM_CLASSES):
            return
        group = item._eve_type.group
        # Ignore items, whose eve type isn't assigned
        # to any group
        if group is None:
            return
        # Having group ID is sufficient condition
        # to enter container of all fitted items
        self.__group_all.add_data(group, item)
        # To enter restriction container, eve type
        # must have restriction attribute
        if self.__max_group_attr not in item._eve_type.attributes:
            return
        self.__group_restricted.add(item)

    def _unregister_item(self, item):
        # Just clear data containers
        group = item._eve_type.group
        self.__group_all.rm_data(group, item)
        self.__group_restricted.discard(item)

    def validate(self):
        # Container for tainted items
        tainted_items = {}
        # Go through all restricted items
        for item in self.__group_restricted:
            # Get number of registered items, assigned to group of current
            # restricted item, and item's restriction value
            group = item._eve_type.group
            group_items = len(self.__group_all.get(group, ()))
            max_group_restriction = item._eve_type.attributes[self.__max_group_attr]
            # If number of registered items from this group is bigger,
            # then current item is tainted
            if group_items > max_group_restriction:
                tainted_items[item] = MaxGroupErrorData(
                    item_group=group,
                    max_group=max_group_restriction,
                    group_items=group_items
                )
        # Raise error if we detected any tainted items
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return self.__restriction_type


class MaxGroupFittedRestriction(MaxGroupRestriction):
    """
    Implements restriction:
    If item has max group fitted restriction, number of fitted
    items of this group should not exceed restriction value,
    else item with such restriction is tainted.

    Details:
    Only module-class items are restricted.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self, fit):
        MaxGroupRestriction.__init__(self, Attribute.max_group_fitted, Restriction.max_group_fitted)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        MaxGroupRestriction._register_item(self, message.item)

    def _handle_item_removal(self, message):
        MaxGroupRestriction._unregister_item(self, message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }


class MaxGroupOnlineRestriction(MaxGroupRestriction):
    """
    Implements restriction:
    If item has max group online restriction, number of online
    items of this group should not exceed restriction value,
    else item with such restriction is tainted.

    Details:
    Only module-class items are restricted.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self, fit):
        MaxGroupRestriction.__init__(self, Attribute.max_group_online, Restriction.max_group_online)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_states_activation(self, message):
        if State.online in message.states:
            MaxGroupRestriction._register_item(self, message.item)

    def _handle_item_states_deactivation(self, message):
        if State.online in message.states:
            MaxGroupRestriction._unregister_item(self, message.item)

    _handler_map = {
        InstrStatesActivate: _handle_item_states_activation,
        InstrStatesDeactivate: _handle_item_states_deactivation
    }


class MaxGroupActiveRestriction(MaxGroupRestriction):
    """
    Implements restriction:
    If item has max group active restriction, number of active
    items of this group should not exceed restriction value,
    else item with such restriction is tainted.

    Details:
    Only module-class items are restricted.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self, fit):
        MaxGroupRestriction.__init__(self, Attribute.max_group_active, Restriction.max_group_active)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_states_activation(self, message):
        if State.active in message.states:
            MaxGroupRestriction._register_item(self, message.item)

    def _handle_item_states_deactivation(self, message):
        if State.active in message.states:
            MaxGroupRestriction._unregister_item(self, message.item)

    _handler_map = {
        InstrStatesActivate: _handle_item_states_activation,
        InstrStatesDeactivate: _handle_item_states_deactivation
    }
