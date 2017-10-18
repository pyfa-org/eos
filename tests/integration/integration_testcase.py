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


from copy import copy

from eos.const.eve import GroupId, TypeId
from eos.data.source import Source, SourceManager
from eos.eve_object.modifier import DogmaModifier
from tests.eos_testcase import EosTestCase


class IntegrationTestCase(EosTestCase):
    """Test case class is used by integration tests.

    Supports almost end-to-end testing of Eos, leaving only data handler, cache
    handler and eve object builder outside of scope.

    Sets up two sources for fit, src1 (default) and src2.

    Attributes:
        ch2: Cache handler for second source.
    """

    def setUp(self):
        super().setUp()
        self.ch2 = self._make_cache_handler()
        # Replace existing sources with test source
        self.__backup_sources = copy(SourceManager._sources)
        self.__backup_default_source = SourceManager.default
        SourceManager._sources.clear()
        self.__make_source('src1', self.ch, make_default=True)
        self.__make_source('src2', self.ch2)

    def tearDown(self):
        # Revert source change
        SourceManager._sources.clear()
        SourceManager._sources.update(self.__backup_sources)
        SourceManager.default = self.__backup_default_source
        super().tearDown()

    def __make_source(self, alias, cache_handler, make_default=False):
        source = Source(alias, cache_handler)
        # Add source 'manually' to avoid building cache
        SourceManager._sources[alias] = source
        if make_default is True:
            SourceManager.default = source
        # Instantiate character type, as it's used in every test
        cache_handler.type(
            type_id=TypeId.character_static, group=GroupId.character)
        return source

    def mod(self, *args, **kwargs):
        """Shortcut to instantiating dogma modifier."""
        return DogmaModifier(*args, **kwargs)

    def allocate_type_id(self, *cache_handlers):
        return max(ch.allocate_type_id() for ch in cache_handlers)

    def allocate_attribute_id(self, *cache_handlers):
        return max(ch.allocate_attr_id() for ch in cache_handlers)

    def allocate_effect_id(self, *cache_handlers):
        return max(ch.allocate_effect_id() for ch in cache_handlers)

    def assert_fit_buffers_empty(self, fit, clear_all=True):
        """Checks if fit contains anything in object containers.

        Args:
            fit: Fit to verify.
            clear_all (optional): Before checking, by default fit has all its
                items removed. If necessary, they can be kept. Please note, that
                character item is always removed anyway.

        Only containers which are designed to hold temporary data are checked.
        """
        self.__clear_fit(fit, clear_all)
        entry_num = 0
        # As volatile manager always has one entry added to it, stats service,
        # make sure it's ignored for assertion purposes
        fit._volatile_mgr._FitVolatileManager__volatile_objects.remove(
            fit.stats)
        entry_num += self._get_object_buffer_entry_amount(
            fit,
            ignore_objects=[fit],
            ignore_attrs=(
                ('Fit', '_Fit__source'),
                ('Fit', '_Fit__default_incoming_damage'),
                ('Fit', '_FitMessageBroker__subscribers'),
                ('RestrictionService', '_RestrictionService__restrictions'),
                ('StatService', '_StatService__volatile_containers')))
        if entry_num:
            plu = 'y' if entry_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(
                entry_num, plu)
            self.fail(msg=msg)

    def __clear_fit(self, fit, clear_all):
        fit.character = None
        if clear_all:
            fit.ship = None
            fit.stance = None
            fit.effect_beacon = None
            fit.subsystems.clear(),
            fit.modules.high.clear(),
            fit.modules.med.clear(),
            fit.modules.low.clear(),
            fit.rigs.clear(),
            fit.drones.clear(),
            fit.fighters.clear(),
            fit.skills.clear(),
            fit.implants.clear(),
            fit.boosters.clear()
        fit._volatile_mgr._FitVolatileManager__clear_volatile_attrs()
