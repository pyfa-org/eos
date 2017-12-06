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


from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.eve_object import DogmaModifier


def make_mass_modifier():
    mass_modifier = DogmaModifier(
        tgt_filter=ModTgtFilter.item,
        tgt_domain=ModDomain.ship,
        tgt_attr_id=AttrId.mass,
        operator=ModOperator.mod_add,
        src_attr_id=AttrId.mass_addition)
    return mass_modifier


def make_signature_modifier():
    signature_modifier = DogmaModifier(
        tgt_filter=ModTgtFilter.item,
        tgt_domain=ModDomain.ship,
        tgt_attr_id=AttrId.signature_radius,
        operator=ModOperator.post_percent,
        src_attr_id=AttrId.signature_radius_bonus)
    return signature_modifier
