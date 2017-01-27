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


__all__ = [
    'ItemAdded',
    'ItemRemoved',
    'ItemStateChanged',
    'EffectsEnabled',
    'EffectsDisabled',
    'AttrValueChanged',
    'AttrValueChangedOverride',
    'EnableServices',
    'DisableServices',
    'RefreshSource'
]


# Item-related messages
ItemAdded = namedtuple('ItemAdded', ('item',))
ItemRemoved = namedtuple('ItemRemoved', ('item',))
ItemStateChanged = namedtuple('ItemStateChanged', ('item', 'old', 'new'))
EffectsEnabled = namedtuple('EffectsEnabled', ('item', 'effects'))
EffectsDisabled = namedtuple('EffectsDisabled', ('item', 'effects'))
# Attribute-related
AttrValueChanged = namedtuple('AttrValueChanged', ('item', 'attr'))
AttrValueChangedOverride = namedtuple('AttrValueChangedOverride', ('item', 'attr'))
# Source change-related
EnableServices = namedtuple('EnableServices', ('items',))
DisableServices = namedtuple('DisableServices', ('items',))
RefreshSource = namedtuple('RefreshSource', ())
