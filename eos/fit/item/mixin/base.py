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


from abc import ABCMeta, abstractmethod
from collections import namedtuple
from random import random

from eos.const.eos import EffectRunMode, State
from eos.fit.calculator import MutableAttributeMap
from eos.fit.pubsub.message import InputItemAdded, InputItemRemoved, InputEffectsStatusChanged, InstrRefreshSource
from eos.fit.pubsub.subscriber import BaseSubscriber


EffectData = namedtuple('EffectData', ('effect', 'chance', 'activable'))
DEFAULT_EFFECT_MODE = EffectRunMode.full_compliance


class BaseItemMixin(BaseSubscriber, metaclass=ABCMeta):
    """
    Base item class which provides all the data needed for attribute
    calculation to work properly. Not directly subclassed by items,
    but by other mixins (which implement concrete functionality over
    it).

    Required arguments:
    type_id -- ID of eve type ID which should serve as base for this
        item

    Cooperative methods:
    __init__
    """

    def __init__(self, type_id, **kwargs):
        self._eve_type_id = type_id
        # Which container this item is placed to
        self.__container = None
        # Special dictionary subclass that holds modified attributes
        # and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Contains IDs of effects which are prohibited to be activated on this item.
        # IDs are stored here without actual effects because we want to keep blocked
        # effect info even when item's fit switches sources
        self.__blocked_effect_ids = set()
        # Container for effects IDs which are currently running
        self._running_effects = set()
        # Keeps track of effect run modes, if they are any different from default
        # Format: {effect ID: effect run mode}
        self.__effect_mode_overrides = None
        # Which eve type this item wraps. Use null source item by default,
        # as item doesn't have fit with source yet
        self._eve_type = None
        super().__init__(**kwargs)

    @property
    def _container(self):
        return self.__container

    @_container.setter
    def _container(self, new_container):
        charge = getattr(self, 'charge', None)
        old_fit = self._fit
        if old_fit is not None:
            # Unlink fit and contained items first
            if charge is not None:
                old_fit._unsubscribe(charge, charge._handler_map.keys())
                old_fit._publish(InputItemRemoved(charge))
            # Then unlink fit and item itself
            old_fit._unsubscribe(self, self._handler_map.keys())
            old_fit._publish(InputItemRemoved(self))
        self.__container = new_container
        self._refresh_source()
        if charge is not None:
            charge._refresh_source()
        # New fit
        new_fit = self._fit
        if new_fit is not None:
            # Link fit and item itself first
            new_fit._publish(InputItemAdded(self))
            new_fit._subscribe(self, self._handler_map.keys())
            # Then link fit and contained items
            if charge is not None:
                new_fit._publish(InputItemAdded(charge))
                new_fit._subscribe(charge, charge._handler_map.keys())

    @property
    def _container_position(self):
        """
        Index of the item within parent container. Should return
        position only for ordered containers.
        """
        try:
            return self._container.index(self)
        except AttributeError:
            return None

    @property
    def _fit(self):
        try:
            return self._container._fit
        except AttributeError:
            return None

    @property
    @abstractmethod
    def state(self):
        ...

    # Properties used by attribute calculator
    @property
    @abstractmethod
    def _parent_modifier_domain(self):
        ...

    @property
    @abstractmethod
    def _owner_modifiable(self):
        ...

    @property
    def _other(self):
        container = self._container
        if isinstance(container, BaseItemMixin):
            return container
        else:
            return None

    # Old effect methods
    @property
    def _effects_data(self):
        """
        Return map with effects and their item-specific data.

        Return data as dictionary:
        {effect ID: (effect=effect object, chance=chance to apply
            on effect activation, activable=activable flag)}
        """
        try:
            eve_type_effects = self._eve_type.effects
        except AttributeError:
            return {}
        data = {}
        for effect in eve_type_effects.values():
            # Get chance from modified attributes, if specified
            chance = effect.get_fitting_usage_chance(self)
            # Get effect activable flag
            activable = effect.id not in self.__blocked_effect_ids
            data[effect.id] = EffectData(effect, chance, activable)
        return data

    def _set_effect_activability(self, effect_id, activability):
        """
        Set activability of particular effect.
        """
        self.__set_effects_activability({effect_id: activability})

    def __set_effects_activability(self, effect_activability):
        """
        Set activability of effects for this item.

        Required arguments:
        effect_activability -- dictionary in the form of {effect ID:
            activability flag}. Activability flag controls if effect
            should be set as activable or blocked.
        """
        changes = {}
        for effect_id, activability in effect_activability.items():
            if activability and effect_id in self.__blocked_effect_ids:
                changes[effect_id] = activability
                self.__blocked_effect_ids.remove(effect_id)
            elif not activability and effect_id not in self.__blocked_effect_ids:
                changes[effect_id] = activability
                self.__blocked_effect_ids.add(effect_id)
        if len(changes) == 0:
            return
        fit = self._fit
        if fit is not None:
            fit._publish(InputEffectsStatusChanged(self, changes))

    def _randomize_effects_status(self, effect_filter=None):
        """
        Randomize status of effects on this item, take value of
        chance attribute into consideration when necessary.

        Optional arguments:
        effect_filter -- randomize statuses of effects whose IDs
            are in this iterable. When None, randomize all
            effects. Default is None.
        """
        effect_activability = {}
        for effect_id, data in self._effects_data.items():
            if effect_filter is not None and effect_id not in effect_filter:
                continue
            # If effect is not chance-based, it always gets run
            if data.chance is None:
                effect_activability[effect_id] = True
                continue
            # If it is, roll the floating dice
            if random() < data.chance:
                effect_activability[effect_id] = True
            else:
                effect_activability[effect_id] = False
        self.__set_effects_activability(effect_activability)

    @property
    def _activable_effects(self):
        try:
            eve_type_effects = self._eve_type.effects
        except AttributeError:
            return {}
        return {eid: e for eid, e in eve_type_effects.items() if eid not in self.__blocked_effect_ids}

    @property
    @abstractmethod
    def _active_effects(self):
        ...

    # Effect methods
    def _get_effect_run_status_changes(self):
        to_run = set()
        to_stop = set()
        try:
            eve_type_effects = self._eve_type.effects
        # If eve type effects are not accessible, then we cannot
        # do anything, as we rely on effect attributes to take
        # our decisions
        except AttributeError:
            return to_run, to_stop
        # Reference some data locally for faster access
        effect_run_modes = self._effect_run_modes
        item_state = self.state
        for effect_id, effect in eve_type_effects.items():
            # Flag which controls if currently reviewed effect should
            # be running or not. Assume it's not by default
            effect_running = False
            # Decide how we handle effect based on its run mode
            effect_run_mode = effect_run_modes[effect_id]
            if effect_run_mode == EffectRunMode.full_compliance:
                # Check state restriction first, as it should be checked
                # regardless of effect category
                effect_state = effect._state
                if item_state >= effect_state:
                    # Offline effects must NOT specify fitting usage chance
                    if effect_state == State.offline:
                        if effect.fitting_usage_chance_attribute is None:
                            effect_running = True
                    # Online effects are running only in presence of running
                    # 'online' effect
                    elif effect_state == State.online:
                        # TODO
                        pass
                    # Only default active effect is run in full compliance
                    elif effect_state == State.active:
                        if self._eve_type.default_effect is effect:
                            effect_running = True
                    # No additional restrictions for overload effects
                    elif effect_state == State.overload:
                        effect_running = True
            # In state compliance, consider effect running if item's
            # state is at least as high as required by the effect
            elif effect_run_mode == EffectRunMode.state_compliance:
                if item_state >= effect._state:
                    effect_running = True
            # If it's supposed to always run, make it so without
            # a second thought
            elif effect_run_mode == EffectRunMode.force_run:
                effect_running = True
            # Do nothing if effect is supposed to not run, we have
            # this status by default anyway
            elif effect_run_mode == EffectRunMode.force_stop:
                pass

    @property
    def _effect_run_modes(self):
        overrides = self.__effect_mode_overrides or {}
        # Copy to not expose overrides map itself to caller
        effect_modes = dict(overrides)
        try:
            eve_type_effects = self._eve_type.effects
        # If effect data on item is not available, return just overrides
        except AttributeError:
            return effect_modes
        # If item has effects, fill mode map with missing effects
        # with default mode assigned
        else:
            for effect_id in eve_type_effects:
                if effect_id in overrides:
                    continue
                effect_modes[effect_id] = DEFAULT_EFFECT_MODE
            return effect_modes

    def _get_effect_run_mode(self, effect_id):
        """
        Get run mode for passed effect ID. Returns run mode even if
        there's no such effect on item (default mode in such case).
        """
        if self.__effect_mode_overrides is None:
            return DEFAULT_EFFECT_MODE
        return self.__effect_mode_overrides.get(effect_id, DEFAULT_EFFECT_MODE)

    def _set_effects_run_modes(self, effects_modes):
        """
        Set modes of multiple effects for this item.

        Required arguments:
        effects_modes -- map in the form of {effect ID: effect run mode}.
        """
        for effect_id, effect_mode in effects_modes.items():
            ...

    def _set_effect_run_mode(self, effect_id, new_mode):
        """
        Set run mode for passed effect.
        """
        # If it's default, then remove it from override map
        if new_mode == DEFAULT_EFFECT_MODE:
            # If override map is not initialized, we're not changing
            # anything
            if self.__effect_mode_overrides is None:
                return
            # Try removing value from override map and do nothing if it
            # fails. It means that default mode was requested for an
            # effect for which getter will return default anyway
            try:
                del self.__effect_mode_overrides[effect_id]
            except KeyError:
                pass
            # If we removed value, replace dict with None to save memory
            else:
                if len(self.__effect_mode_overrides) == 0:
                    self.__effect_mode_overrides = None
        # If value is not default, initialize override map if necessary
        # and store value
        else:
            if self.__effect_mode_overrides is None:
                self.__effect_mode_overrides = {}
            self.__effect_mode_overrides[effect_id] = new_mode

    # Message handling
    def _handle_refresh_source(self, _):
        self._refresh_source()

    _handler_map = {
        InstrRefreshSource: _handle_refresh_source
    }

    # Private methods for message handlers
    def _refresh_source(self):
        """
        Each time item's context is changed (the source it relies on,
        which may change when item switches fit or its fit switches
        source), this method should be called; it will refresh data
        which is source-dependent.
        """
        self.attributes.clear()
        try:
            type_getter = self._fit.source.cache_handler.get_type
        # When we're asked to refresh source, but we have no fit or
        # fit has no valid source assigned, we assign NullSource object
        # as eve type - it's needed to raise errors on access to source-
        # dependent stuff
        except AttributeError:
            self._eve_type = None
        else:
            self._eve_type = type_getter(self._eve_type_id)
