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


from abc import ABCMeta, abstractmethod

from eos.const.eos import EffectRunMode, State
from eos.const.eve import EffectId
from eos.fit.calculator import MutableAttributeMap
from eos.fit.pubsub.message import (
    InputEffectsRunModeChanged, InputItemAdded, InputItemRemoved,
    InstrRefreshSource
)
from eos.fit.pubsub.subscriber import BaseSubscriber


DEFAULT_EFFECT_MODE = EffectRunMode.full_compliance


class BaseItemMixin(BaseSubscriber, metaclass=ABCMeta):
    """Base class for all items.

    It provides all the data needed for attribute calculation to work properly.
    Not directly subclassed by items, but by other mixins (which implement
    concrete functionality over it).

    Args:
        type_id: Identifier of eve type which should serve as base for this
            item.

    Cooperative methods:
        __init__
    """

    def __init__(self, type_id, **kwargs):
        self._eve_type_id = type_id
        self.__container = None
        # Special dictionary subclass that holds modified attributes and data
        # related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Container for effects IDs which are currently running
        self._running_effects = set()
        # Effect run modes, if they are any different from default
        # Format: {effect ID: effect run mode}
        self.__effect_mode_overrides = None
        # Which eve type this item wraps. Use null source item by default, as
        # item doesn't have fit with source yet
        self._eve_type = None
        super().__init__(**kwargs)

    @property
    def _container(self):
        """Refers container this item is placed to.

        Can be other fit, various container classes or other item.
        """
        return self.__container

    @_container.setter
    def _container(self, new_container):
        charge = getattr(self, 'charge', None)
        # Old fit section
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
        # New fit section
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
        """Index of the item within parent container.

        Returns: Position within parent ordered container. If item is not
        assigned or container is not ordered, returns None.
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

    # Effect methods
    def _get_wanted_effect_run_status_changes(self):
        """Get changes needed to actualize effect running statuses.

        Returns: Tuple with two sets, first with effect IDs which should be
        started and second with effect IDss which should be stopped to achieve
        proper state.
        """
        try:
            eve_type_effects = self._eve_type.effects
        # If eve type effects are not accessible, then we cannot do anything, as
        # we rely on effect attributes to take our decisions
        except AttributeError:
            return set(), set()
        # Set of effects which should be running according to new conditions
        new_running = set()
        # Process 'online' effect separately, as it's needed for all other
        # effects from online categories
        if EffectId.online in eve_type_effects:
            online_running = self.__get_wanted_effect_run_status(
                eve_type_effects[EffectId.online], None)
            if online_running is True:
                new_running.add(EffectId.online)
        else:
            online_running = False
        # Do a pass over regular effects
        for effect_id, effect in eve_type_effects.items():
            if effect_id == EffectId.online:
                continue
            if self.__get_wanted_effect_run_status(effect, online_running):
                new_running.add(effect_id)
        to_start = new_running.difference(self._running_effects)
        to_stop = self._running_effects.difference(new_running)
        return to_start, to_stop

    def __get_wanted_effect_run_status(self, effect, online_running):
        """Decide if effect should be running or not.

        Decision is taken based on effect's run mode, item's state and multiple
        less significant factors.

        Args:
            effect: Effect in question.
            online_running: Flag which tells us if 'online' effect is running on
                this item or not.
        """
        # Decide how we handle effect based on its run mode
        effect_run_mode = self.get_effect_run_mode(effect.id)
        if effect_run_mode == EffectRunMode.full_compliance:
            # Check state restriction first, as it should be checked regardless
            # of effect category
            effect_state = effect._state
            if self.state < effect_state:
                return False
            # Offline effects must NOT specify fitting usage chance
            if effect_state == State.offline:
                return effect.fitting_usage_chance_attribute is None
            # Online effects depend on 'online' effect
            elif effect_state == State.online:
                # If we've been requested 'online' effect status, it has no
                # additional restrictions
                if effect.id == EffectId.online:
                    return True
                # For regular online effects, check if 'online' is running
                else:
                    return online_running
            # Only default active effect is run in full compliance
            elif effect_state == State.active:
                return self._eve_type.default_effect is effect
            # No additional restrictions for overload effects
            elif effect_state == State.overload:
                return True
            # For safety, generally should never happen
            else:
                return False
        # In state compliance, consider effect running if item's state is at
        # least as high as required by the effect
        elif effect_run_mode == EffectRunMode.state_compliance:
            return self.state >= effect._state
        # If it's supposed to always run, make it so without a second thought
        elif effect_run_mode == EffectRunMode.force_run:
            return True
        # Same for always-stop
        elif effect_run_mode == EffectRunMode.force_stop:
            return False
        # For safety, generally should never happen
        else:
            return False

    def get_effect_run_mode(self, effect_id):
        if self.__effect_mode_overrides is None:
            return DEFAULT_EFFECT_MODE
        return self.__effect_mode_overrides.get(effect_id, DEFAULT_EFFECT_MODE)

    def set_effect_run_mode(self, effect_id, new_mode):
        self._set_effects_run_modes({effect_id: new_mode})

    def _set_effects_run_modes(self, effects_modes):
        """
        Set modes of multiple effects for this item.

        Args:
            effects_modes: Map in the form of {effect ID: effect run mode}.
        """
        for effect_id, effect_mode in effects_modes.items():
            # If new mode is default, then remove it from override map
            if effect_mode == DEFAULT_EFFECT_MODE:
                # If override map is not initialized, we're not changing
                # anything
                if self.__effect_mode_overrides is None:
                    return
                # Try removing value from override map and do nothing if it
                # fails. It means that default mode was requested for an effect
                # for which getter will return default anyway
                try:
                    del self.__effect_mode_overrides[effect_id]
                except KeyError:
                    pass
            # If value is not default, initialize override map if necessary and
            # store value
            else:
                if self.__effect_mode_overrides is None:
                    self.__effect_mode_overrides = {}
                self.__effect_mode_overrides[effect_id] = effect_mode
        # After all the changes we did, check if there's any data in overrides
        # map, if there's no data, replace it with None to save memory
        if not self.__effect_mode_overrides:
            self.__effect_mode_overrides = None
        fit = self._fit
        if fit is not None:
            fit._publish(InputEffectsRunModeChanged(self))

    # Message handling
    def _handle_refresh_source(self, _):
        self._refresh_source()

    _handler_map = {
        InstrRefreshSource: _handle_refresh_source
    }

    # Private methods for message handlers
    def _refresh_source(self):
        """Refresh item's source-dependent data.

        Each time item's context is changed (the source it relies on, which may
        change when item switches fit or its fit switches source), this method
        should be called.
        """
        self.attributes.clear()
        try:
            type_getter = self._fit.source.cache_handler.get_type
        except AttributeError:
            self._eve_type = None
        else:
            self._eve_type = type_getter(self._eve_type_id)
