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


from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple

from eos.const.eos import EffectMode
from eos.fit.calculator import MutableAttrMap
from eos.fit.item_container import ItemDict
from eos.fit.message.helper import MsgHelper


DEFAULT_EFFECT_MODE = EffectMode.full_compliance


EffectData = namedtuple('EffectData', ('effect', 'mode', 'status'))


class BaseItemMixin(metaclass=ABCMeta):
    """Base class for all items.

    It provides all the data needed for attribute calculation to work properly.
    Not directly subclassed by items, but by other mixins (which implement
    concrete functionality over it).

    Args:
        type_id: Identifier of item type which should serve as base for this
            item.

    Cooperative methods:
        __init__
        _get_child_items
    """

    def __init__(self, type_id, **kwargs):
        self._type_id = type_id
        # Which item type this item based on
        self._type = None
        # Container for effects IDs which are currently running
        self._running_effect_ids = set()
        # Effect run modes, if they are any different from default
        # Format: {effect ID: effect run mode}
        self.__effect_mode_overrides = None
        # Special dictionary subclass that holds modified attributes and data
        # related to their calculation
        self.attrs = MutableAttrMap(self)
        # Charges which are 'auto-loaded' into item by effects
        # Format: {effect ID: autocharge type ID}
        self.__autocharges = None
        self._container = None
        super().__init__(**kwargs)

    def _get_child_items(self):
        try:
            child_getter = super()._get_child_items
        except AttributeError:
            child_items = set()
        else:
            child_items = child_getter()
        child_items.update(self.autocharges.values())
        return child_items

    @property
    def _container_position(self):
        """Index of the item within parent container.

        Returns:
            Position within parent ordered container. If item is not assigned or
            container is not ordered, returns None.
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

    # Properties which expose various item type properties with safe fallback
    @property
    def _type_attrs(self):
        try:
            return self._type.attrs
        except AttributeError:
            return {}

    @property
    def _type_effects(self):
        try:
            return self._type.effects
        except AttributeError:
            return {}

    @property
    def _type_default_effect(self):
        try:
            return self._type.default_effect
        except AttributeError:
            return None

    @property
    def _type_default_effect_id(self):
        try:
            return self._type.default_effect.id
        except AttributeError:
            return None

    # Properties used by attribute calculator
    @property
    @abstractmethod
    def _modifier_domain(self):
        ...

    @property
    @abstractmethod
    def _owner_modifiable(self):
        ...

    @property
    def _others(self):
        other_items = set()
        container = self._container
        if isinstance(container, BaseItemMixin):
            other_items.add(container)
        other_items.update(self._get_child_items())
        return other_items

    # Effect methods
    @property
    def effects(self):
        """Expose item's effects with item-specific data.

        Returns:
            Map in format {effect ID: (effect, effect run mode, effect run
            status)}.
        """
        effects = {}
        for effect_id, effect in self._type_effects.items():
            mode = self.get_effect_mode(effect_id)
            status = effect_id in self._running_effect_ids
            effects[effect_id] = EffectData(effect, mode, status)
        return effects

    def get_effect_mode(self, effect_id):
        """Get effect's run mode for this item."""
        if self.__effect_mode_overrides is None:
            return DEFAULT_EFFECT_MODE
        return self.__effect_mode_overrides.get(effect_id, DEFAULT_EFFECT_MODE)

    def set_effect_mode(self, effect_id, effect_mode):
        """Set effect's run mode for this item."""
        self._set_effects_modes({effect_id: effect_mode})

    def _set_effects_modes(self, effects_modes):
        """
        Set modes of multiple effects for this item.

        Args:
            effects_modes: Map in {effect ID: effect run mode} format.
        """
        for effect_id, effect_mode in effects_modes.items():
            # If new mode is default, then remove it from override map
            if effect_mode == DEFAULT_EFFECT_MODE:
                # If override map is not initialized, we're not changing
                # anything
                if self.__effect_mode_overrides is None:
                    continue
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
        if (
            self.__effect_mode_overrides is not None and
            len(self.__effect_mode_overrides) == 0
        ):
            self.__effect_mode_overrides = None
        fit = self._fit
        if fit is not None and fit.source is not None:
            msgs = MsgHelper.get_effects_status_update_msgs(self)
            if msgs:
                fit._publish_bulk(msgs)

    # Autocharge methods
    @property
    def autocharges(self):
        """Returns map which contains charges, 'autoloaded' by effects.

        These charges will always be on item as long as item type defines them.
        """
        # Format {effect ID: charge}
        return self.__autocharges or {}

    def _add_autocharge(self, effect_id, autocharge_type_id):
        # Using import here is ugly, but there's no good way to use subclass
        # within parent class. Other solution is to create method on fit and
        # call that method, but fit shouldn't really care about implementation
        # details of items too
        from eos.fit.item.charge import Autocharge
        if self.__autocharges is None:
            self.__autocharges = ItemDict(
                self, Autocharge, container_override=self)
        self.__autocharges[effect_id] = Autocharge(autocharge_type_id)

    def _clear_autocharges(self):
        if self.__autocharges is not None:
            self.__autocharges.clear()
            self.__autocharges = None

    # Auxiliary methods
    def _refresh_source(self):
        """Refresh item's source-dependent data.

        Each time item's context is changed (the source it relies on, which may
        change when item switches fit or its fit switches source), this method
        should be called.
        """
        self.attrs.clear()
        self._clear_autocharges()
        try:
            type_getter = self._fit.source.cache_handler.get_type
        except AttributeError:
            self._type = None
        else:
            self._type = type_getter(self._type_id)
            # Add autocharges, if effects specify any
            for effect_id, effect in self._type_effects.items():
                autocharge_type_id = effect.get_autocharge_type_id(self)
                if autocharge_type_id is None:
                    continue
                self._add_autocharge(effect_id, autocharge_type_id)
