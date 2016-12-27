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


__all__ = [
    'HolderAdded',
    'HolderRemoved',
    'HolderStateChanged',
    'EffectsEnabled',
    'EffectsDisabled',
    'EnableServices',
    'DisableServices',
    'RefreshSource',
    'AttrOverrideChanged'
]


# Holder-related messages
HolderAdded = namedtuple('HolderAdded', ('holder',))
HolderRemoved = namedtuple('HolderRemoved', ('holder',))
HolderStateChanged = namedtuple('HolderStateChanged', ('holder', 'old', 'new'))
EffectsEnabled = namedtuple('EffectsEnabled', ('holder', 'effects'))
EffectsDisabled = namedtuple('EffectsDisabled', ('holder', 'effects'))
# Source change-related
EnableServices = namedtuple('EnableServices', ('holders',))
DisableServices = namedtuple('DisableServices', ('holders',))
RefreshSource = namedtuple('RefreshSource', ())
# Misc
AttrOverrideChanged = namedtuple('AttrOverrideChanged', ('holder', 'attr', 'old', 'new'))
