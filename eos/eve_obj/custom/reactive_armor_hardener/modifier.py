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
from eos.const.eos import ModAggregateMode
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eve import AttrId
from eos.eve_obj.modifier import DogmaModifier


def make_rah_modifiers():
    rah_modifiers = tuple(
        DogmaModifier(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=attr_id,
            operator=ModOperator.pre_mul,
            aggregate_mode=ModAggregateMode.stack,
            affector_attr_id=attr_id)
        for attr_id in (
            AttrId.armor_em_dmg_resonance,
            AttrId.armor_therm_dmg_resonance,
            AttrId.armor_kin_dmg_resonance,
            AttrId.armor_expl_dmg_resonance))
    return rah_modifiers
