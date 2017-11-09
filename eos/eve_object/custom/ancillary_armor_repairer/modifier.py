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


from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import AttributeId, TypeId
from eos.fit.message import AttrValueChanged, ItemAdded, ItemRemoved
from ...modifier.exception import ModificationCalculationError
from ...modifier.python import BasePythonModifier


class AncillaryRepAmountModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self, tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self, tgt_filter_extra_arg=None,
            tgt_attr_id=AttributeId.armor_damage_amount)

    def get_modification(self, carrier_item, _):
        # If carrier item has charge and it's paste, use on-carrier rep amount
        # multiplier, otherwise do nothing (multipy by 1).
        charge = getattr(carrier_item, 'charge', None)
        if (
            charge is not None and
            charge._type_id == TypeId.nanite_repair_paste
        ):
            try:
                multiplier = (
                    carrier_item.attributes
                    [AttributeId.charged_armor_damage_multiplier])
            except (AttributeError, KeyError) as e:
                raise ModificationCalculationError from e
        else:
            multiplier = 1
        return ModifierOperator.post_mul_immune, multiplier

    def __revise_on_item_added_removed(self, message, carrier_item, _):
        # If added/removed item is charge of effect carrying item and charge is
        # paste, then modification value changes
        if (
            getattr(carrier_item, 'charge', None) is message.item and
            message.item._type_id == TypeId.nanite_repair_paste
        ):
            return True
        return False

    def __revise_on_attr_changed(self, message, carrier_item, _):
        # If armor rep multiplier changes, then result of modification also
        # should change
        if (
            message.item is carrier_item and
            message.attr == AttributeId.charged_armor_damage_multiplier
        ):
            return True
        return False

    __revision_map = {
        ItemAdded: __revise_on_item_added_removed,
        ItemRemoved: __revise_on_item_added_removed,
        AttrValueChanged: __revise_on_attr_changed}

    @property
    def revise_message_types(self):
        return set(self.__revision_map.keys())

    def revise_modification(self, message, carrier_item, ship):
        revision_func = self.__revision_map[type(message)]
        return revision_func(self, message, carrier_item, ship)
