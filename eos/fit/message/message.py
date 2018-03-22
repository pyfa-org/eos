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


from eos.util.repr import make_repr_str


class ItemLoaded:

    def __init__(self, item):
        self.item = item

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class ItemUnloaded:

    def __init__(self, item):
        self.item = item

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class StatesActivated:

    def __init__(self, item, states):
        self.item = item
        # Format: {states}
        self.states = states

    def __repr__(self):
        spec = ['item', 'states']
        return make_repr_str(self, spec)


class StatesDeactivated:

    def __init__(self, item, states):
        self.item = item
        # Format: {states}
        self.states = states

    def __repr__(self):
        spec = ['item', 'states']
        return make_repr_str(self, spec)


class EffectsStarted:

    def __init__(self, item, effect_ids):
        self.item = item
        # Format: {effect IDs}
        self.effect_ids = effect_ids

    def __repr__(self):
        spec = ['item', 'effect_ids']
        return make_repr_str(self, spec)


class EffectsStopped:

    def __init__(self, item, effect_ids):
        self.item = item
        # Format: {effect IDs}
        self.effect_ids = effect_ids

    def __repr__(self):
        spec = ['item', 'effect_ids']
        return make_repr_str(self, spec)


class AttrValueChanged:

    def __init__(self, item, attr_id):
        self.item = item
        self.attr_id = attr_id

    def __repr__(self):
        spec = ['item', 'attr_id']
        return make_repr_str(self, spec)


class AttrValueChangedMasked:

    def __init__(self, item, attr_id):
        self.item = item
        self.attr_id = attr_id

    def __repr__(self):
        spec = ['item', 'attr_id']
        return make_repr_str(self, spec)


class DefaultIncomingDmgChanged:

    def __repr__(self):
        return make_repr_str(self)
