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
from random import random

from eos.fit.attribute_calculator import MutableAttributeMap
from .null_source import NullSourceItem


EffectData = namedtuple('EffectData', ('chance', 'status'))


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

    # Effect methods
    @property
    def _effect_data(self):
        """
        Return map with effects and their holder-specific data.

        Return value:
        Dictionary {effect: (chance, status)}
        """
        data = {}
        for effect in self.item.effects:
            # Get chance from modified attributes, if specified
            chance_attr = effect.fitting_usage_chance_attribute
            chance = self.attributes[chance_attr] if chance_attr is not None else None
            # Get effect status
            status = effect.id not in self._disabled_effects
            data[effect] = EffectData(chance, status)
        return data

    def _set_effects_status(self, effect_ids, status):
        """
        Enable or disable effects with IDs from passed list.

        Required arguments:
        effect_ids -- iterable with effect IDs, for which we're
        changing status
        status -- True for enabling, False for disabling
        """
        if status:
            self.__enable_effects(effect_ids)
        else:
            self.__disable_effects(effect_ids)

    def _randomize_effects_status(self, rand_all=True):
        """
        Randomize status of effects on this holder, take value of
        chance attribute into consideration when necessary.

        Optional arguments:
        rand_all -- if True, can change status of all effects on
        this holder, If False, changes status only of chance-
        based effects.
        """
        to_enable = set()
        to_disable = set()
        for effect, data in self._effect_data.items():
            if data.chance is None:
                # If effect is not chance-based, it always gets run.
                # But we are doing it only if we were asked for it.
                if rand_all:
                    to_enable.add(effect.id)
                continue
            # If it is, roll the floating dice
            if random() < data.chance:
                to_enable.add(effect.id)
            else:
                to_disable.add(effect.id)
        self._set_effects_status(to_enable, True)
        self._set_effects_status(to_disable, False)

    @property
    def _enabled_effects(self):
        """Return set with IDs of enabled effects"""
        return set(e.id for e in self.item.effects).difference(self._disabled_effects)

    def __enable_effects(self, effect_ids):
        """
        Enable effects with passed IDs. For effects which
        are already enabled, do nothing.

        Required arguments:
        effect_ids -- iterable with effect IDs to enable
        """
        to_enable = self._disabled_effects.intersection(effect_ids)
        if len(to_enable) == 0:
            return
        self._request_volatile_cleanup()
        self._disabled_effects.difference_update(to_enable)
        self._fit._link_tracker.enable_effects(self, to_enable)

    def __disable_effects(self, effect_ids):
        """
        Disable effects with passed IDs. For effects which
        are already disabled, do nothing.

        Required arguments:
        effect_ids -- iterable with effect IDs to disable
        """
        to_disable = set(effect_ids).difference(self._disabled_effects)
        if len(to_disable) == 0:
            return
        self._request_volatile_cleanup()
        self._fit._link_tracker.disable_effects(self, to_disable)
        self._disabled_effects.update(to_disable)

    # Auxiliary methods
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
