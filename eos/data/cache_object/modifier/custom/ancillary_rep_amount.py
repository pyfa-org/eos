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
from eos.const.eve import Attribute, Type
from eos.fit.messages import ItemAdded, ItemRemoved
from ..python import BasePythonModifier


class AncillaryRepAmountModifier(BasePythonModifier):

    def __init__(self):
        BasePythonModifier.__init__(
            self, state=State.offline, tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self, tgt_filter_extra_arg=None,
            tgt_attr=Attribute.armor_damage_amount
        )

    def get_modification(self, carrier_item, fit):
        """
        If carrier item has charge and it's paste, provide
        modification multiplier 3, otherwise multiplier 1.
        """
        charge = getattr(carrier_item, 'charge', None)
        if charge is not None and charge._eve_type_id == Type.nanite_repair_paste:
            multiplier = 3
        else:
            multiplier = 1
        return ModifierOperator.pre_mul, multiplier

    def _revise_on_item_add_remove(self, message, carrier_item, _):
        """
        If added/removed item is charge of effect carrier and charge
        is paste, then modification value changes.
        """
        if (
            getattr(carrier_item, 'charge', None) is message.item and
            message.item._eve_type_id == Type.nanite_repair_paste
        ):
            return True
        return False

    _revision_map = {
        ItemAdded: _revise_on_item_add_remove,
        ItemRemoved: _revise_on_item_add_remove
    }

    @property
    def revise_message_types(self):
        return set(self._revision_map.keys())

    def revise_modification(self, message, carrier_item, fit):
        revision_func = self._revision_map[type(message)]
        return revision_func(self, message, carrier_item, fit)
