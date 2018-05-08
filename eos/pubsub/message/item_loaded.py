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


from eos.util.repr import make_repr_str


class ItemLoaded:

    def __init__(self, item):
        self.fit = None
        self.item = item

    def __repr__(self):
        spec = ['fit', 'item']
        return make_repr_str(self, spec)


class ItemUnloaded:

    def __init__(self, item):
        self.fit = None
        self.item = item

    def __repr__(self):
        spec = ['fit', 'item']
        return make_repr_str(self, spec)


class StatesActivatedLoaded:

    def __init__(self, item, states):
        self.fit = None
        self.item = item
        # Format: {states}
        self.states = states

    def __repr__(self):
        spec = ['fit', 'item', 'states']
        return make_repr_str(self, spec)


class StatesDeactivatedLoaded:

    def __init__(self, item, states):
        self.fit = None
        self.item = item
        # Format: {states}
        self.states = states

    def __repr__(self):
        spec = ['fit', 'item', 'states']
        return make_repr_str(self, spec)


class EffectsStarted:

    def __init__(self, item, effect_ids):
        self.fit = None
        self.item = item
        # Format: {effect IDs}
        self.effect_ids = effect_ids

    def __repr__(self):
        spec = ['fit', 'item', 'effect_ids']
        return make_repr_str(self, spec)


class EffectsStopped:

    def __init__(self, item, effect_ids):
        self.fit = None
        self.item = item
        # Format: {effect IDs}
        self.effect_ids = effect_ids

    def __repr__(self):
        spec = ['fit', 'item', 'effect_ids']
        return make_repr_str(self, spec)


class EffectsApplied:

    def __init__(self, item, effect_ids):
        self.fit = None
        self.item = item
        # Format: {effect IDs}
        self.effect_ids = effect_ids

    def __repr__(self):
        spec = ['fit', 'item', 'effect_ids']
        return make_repr_str(self, spec)


class EffectsUnapplied:

    def __init__(self, item, effect_ids):
        self.fit = None
        self.item = item
        # Format: {effect IDs}
        self.effect_ids = effect_ids

    def __repr__(self):
        spec = ['fit', 'item', 'effect_ids']
        return make_repr_str(self, spec)
