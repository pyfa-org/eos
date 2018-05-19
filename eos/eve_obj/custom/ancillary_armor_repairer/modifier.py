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
from eos.const.eve import TypeId
from eos.eve_obj.modifier import BasePythonModifier
from eos.eve_obj.modifier import ModificationCalculationError
from eos.pubsub.message import AttrsValueChanged
from eos.pubsub.message import ItemAdded
from eos.pubsub.message import ItemRemoved


class AncillaryRepAmountModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self,
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_filter_extra_arg=None,
            affectee_attr_id=AttrId.armor_dmg_amount)

    def get_modification(self, affector_item):
        # If modifier item has charge and it's paste, use on-item rep amount
        # multiplier, otherwise do nothing (multiply by 1).
        charge = getattr(affector_item, 'charge', None)
        if charge is not None and charge._type_id == TypeId.nanite_repair_paste:
            try:
                value = affector_item.attrs[AttrId.charged_armor_dmg_mult]
            except (AttributeError, KeyError) as e:
                raise ModificationCalculationError from e
        else:
            value = 1
        return ModOperator.post_mul_immune, value

    def __revise_on_item_added_removed(self, msg, affector_item):
        # If added/removed item is charge of effect carrying item and charge is
        # paste, then modification value changes
        if (
            getattr(affector_item, 'charge', None) is msg.item and
            msg.item._type_id == TypeId.nanite_repair_paste
        ):
            return True
        return False

    def __revise_on_attr_changed(self, msg, affector_item):
        # If armor rep multiplier changes, then result of modification also
        # should change
        if (
            affector_item in msg.attr_changes and
            AttrId.charged_armor_dmg_mult in msg.attr_changes[affector_item]
        ):
            return True
        return False

    __revision_map = {
        ItemAdded: __revise_on_item_added_removed,
        ItemRemoved: __revise_on_item_added_removed,
        AttrsValueChanged: __revise_on_attr_changed}

    @property
    def revise_msg_types(self):
        return set(self.__revision_map.keys())

    def revise_modification(self, msg, affector_item):
        revision_func = self.__revision_map[type(msg)]
        return revision_func(self, msg, affector_item)
