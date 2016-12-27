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

from eos.fit.calculator import MutableAttributeMap
from eos.fit.messages import EffectsEnabled, EffectsDisabled, RefreshSource
from eos.util.pubsub import BaseSubscriber
from .null_source import NullSourceItem


EffectData = namedtuple('EffectData', ('effect', 'chance', 'status'))


class HolderBase(BaseSubscriber):
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
        # Contains IDs of effects which are prohibited to be run on this holder.
        # It means that if there's an ID here - it does not mean that holder.item
        # has such effect, but if holder has it, it will be disabled. We need to keep
        # such IDs for case when holder has effect disabled, then it switches source
        # where it doesn't have effect with this ID anymore, then when it switches
        # back - this effect will be disabled like it has been before source switch
        self.__disabled_effects = set()
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
        self.__refresh_source()

    # Effect methods
    @property
    def _effect_data(self):
        """
        Return map with effects and their holder-specific data.

        Return data as dictionary:
        {effect ID: (effect=effect object, chance=chance to apply
        on effect activation, status=effect status)}
        """
        data = {}
        for effect in self.item.effects:
            # Get chance from modified attributes, if specified
            chance_attr = effect.fitting_usage_chance_attribute
            chance = self.attributes[chance_attr] if chance_attr is not None else None
            # Get effect status
            status = effect.id not in self.__disabled_effects
            data[effect.id] = EffectData(effect, chance, status)
        return data

    def _set_effects_status(self, effect_ids, status):
        """
        Enable or disable effects for this holder.

        Required arguments:
        effect_ids -- iterable with effect IDs, for which we're
        changing status
        status -- True for enabling, False for disabling
        """
        if status:
            self.__enable_effects(effect_ids)
        else:
            self.__disable_effects(effect_ids)

    def _randomize_effects_status(self, effect_filter=None):
        """
        Randomize status of effects on this holder, take value of
        chance attribute into consideration when necessary.

        Optional arguments:
        effect_filter -- randomize statuses of effects whose IDs
        are in this iterable. When None, randomize all effects.
        Default is None.
        """
        to_enable = set()
        to_disable = set()
        for effect_id, data in self._effect_data.items():
            if effect_filter is not None and effect_id not in effect_filter:
                continue
            # If effect is not chance-based, it always gets run
            if data.chance is None:
                to_enable.add(effect_id)
                continue
            # If it is, roll the floating dice
            if random() < data.chance:
                to_enable.add(effect_id)
            else:
                to_disable.add(effect_id)
        self._set_effects_status(to_enable, True)
        self._set_effects_status(to_disable, False)

    @property
    def _enabled_effects(self):
        """Return set with IDs of enabled effects"""
        return set(e.id for e in self.item.effects).difference(self.__disabled_effects)

    @property
    def _disabled_effects(self):
        """
        Return set with IDs of effects which exist on this holder
        and are disabled.

        Unlike self.__disabled_effects, this property returns
        IDs of actual effects which are not active on this holder.
        """
        return set(e.id for e in self.item.effects).intersection(self.__disabled_effects)

    def __enable_effects(self, effect_ids):
        """
        Enable effects with passed IDs. For effects which
        are already enabled, do nothing.

        Required arguments:
        effect_ids -- iterable with effect IDs to enable
        """
        to_enable = self.__disabled_effects.intersection(effect_ids)
        if len(to_enable) == 0:
            return
        self.__disabled_effects.difference_update(to_enable)
        if self.__fit is not None:
            self.__fit._publish(EffectsEnabled(self, to_enable))

    def __disable_effects(self, effect_ids):
        """
        Disable effects with passed IDs. For effects which
        are already disabled, do nothing.

        Required arguments:
        effect_ids -- iterable with effect IDs to disable
        """
        to_disable = set(effect_ids).difference(self.__disabled_effects)
        if len(to_disable) == 0:
            return
        if self.__fit is not None:
            self.__fit._publish(EffectsDisabled(self, to_disable))
        self.__disabled_effects.update(to_disable)

    # Message handling
    def _handle_refresh_source(self, message):
        self.__refresh_source()

    _handler_map = {
        RefreshSource: _handle_refresh_source
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Private methods for message handlers
    def __refresh_source(self):
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
