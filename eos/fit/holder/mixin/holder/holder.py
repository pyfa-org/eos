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

from eos.fit.attribute_calculator import MutableAttributeMap
from .null_source import NullSourceItem


EffectData = namedtuple('EffectData', ('chance', 'enabled'))


class HolderBase:
    """
    Base holder class inherited by all classes that
    need to keep track of modified attributes.

    Required arguments:
    type_id -- type ID of item which should serve as base
    for this holder.

    Cooperative methods:
    __init__
    """

    def __init__(self, type_id, **kwargs):
        # TypeID of item this holder is supposed to wrap
        self._type_id = type_id
        # Special dictionary subclass that holds modified attributes
        # and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Which fit this holder is bound to
        self.__fit = None
        # Contains IDs of effects which are prohibited to be run on this holder
        self._disabled_effects = set()
        # Which type this holder wraps. Use null source item by default,
        # as holder doesn't have fit with source yet
        self.item = NullSourceItem
        super().__init__(**kwargs)

    @property
    def _fit(self):
        return self.__fit

    @_fit.setter
    def _fit(self, new_fit):
        self.__fit = new_fit
        self._refresh_source()

    # Effect-related methods
    @property
    def effect_data(self):
        """
        Return map with effects and their holder-specific data.

        Return value:
        Dictionary {effect: (chance, enabled)}
        """
        data = {}
        for effect in self.item.effects:
            # Get chance from modified attributes, if specified
            chance_attr = effect.fitting_usage_chance_attribute
            chance = self.attributes[chance_attr] if chance_attr is not None else None
            # Get effect status
            enabled = effect.id not in self._disabled_effects
            data[effect] = EffectData(chance, enabled)
        return data

    @property
    def _enabled_effects(self):
        """Return set with enabled effects"""
        return set(e.id for e in self.item.effects).difference(self._disabled_effects)

    def _enable_effect(self, effect_id):
        """
        Enable effect with passed ID. If such effect
        is already enabled, do nothing.

        Required arguments:
        effect_id -- ID of effect to disable
        """
        if effect_id not in self._disabled_effects:
            return
        self._disabled_effects.discard(effect_id)
        self._fit._link_tracker.enable_effect(self, effect_id)
        self._request_volatile_cleanup()

    def _disable_effect(self, effect_id):
        """
        Disable effect with passed ID. If such effect
        is already disabled, do nothing.

        Required arguments:
        effect_id -- ID of effect to disable
        """
        if effect_id in self._disabled_effects:
            return
        self._fit._link_tracker.disable_effect(self, effect_id)
        self._disabled_effects.add(effect_id)
        self._request_volatile_cleanup()

    # Misc methods
    def _refresh_source(self):
        """
        Each time holder's context is changed (the source it relies on,
        which may change when holder switches fit or its fit switches
        source), this method should be called; it will refresh data
        which is source-dependent.
        """
        self.attributes.clear()
        try:
            type_getter = self._fit.source.cache_handler.get_type
        # When we're asked to refresh source, but we have no fit or
        # fit has no valid source assigned, we assign NullSource object
        # to an item - it's needed to raise errors on access to source-
        # dependent stuff
        except AttributeError:
            self.item = NullSourceItem
        else:
            self.item = type_getter(self._type_id)

    def _request_volatile_cleanup(self):
        """
        Request fit to clear all fit volatile data.
        """
        fit = self._fit
        if fit is not None:
            fit._request_volatile_cleanup()
