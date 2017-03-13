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


from copy import copy
from itertools import chain

from eos.const.eve import Type, Group
from eos.data.source import SourceManager, Source
from tests.eos_testcase import EosTestCase


class IntegrationTestCase(EosTestCase):
    """
    Additional functionality provided:

    Two sources for fit are set up, src1 (default) and src2
    self.ch2 -- cache handler for second source
    self.assert_fit_buffers_empty -- checks if fit contains anything
        in object containers which are designed to hold temporary data
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
        cache_handler.type(type_id=Type.character_static, group=Group.character)
        return source

    def allocate_type_id(self, *cache_handlers):
        return max(ch.allocate_type_id() for ch in cache_handlers)

    def allocate_attribute_id(self, *cache_handlers):
        return max(ch.allocate_attribute_id() for ch in cache_handlers)

    def allocate_effect_id(self, *cache_handlers):
        return max(ch.allocate_effect_id() for ch in cache_handlers)

    def assert_fit_buffers_empty(self, fit):
        self.__clear_fit(fit)
        entry_num = 0
        # Fit itself
        entry_num += self._get_object_buffer_entry_amount(fit, ignore=(
            '_Fit__source', '_Fit__default_incoming_damage', '_FitMessageBroker__subscribers'
        ))
        # Volatile manager. As volatile manager always has one entry added to it
        # (stats service), make sure it's ignored for assertion purposes
        fit._volatile_mgr._FitVolatileManager__volatile_objects.remove(fit.stats)
        entry_num += self._get_object_buffer_entry_amount(fit._volatile_mgr)
        fit._volatile_mgr._FitVolatileManager__volatile_objects.add(fit.stats)
        # Calculator service
        entry_num += self._get_object_buffer_entry_amount(fit._calculator._CalculationService__affections)
        entry_num += len(fit._calculator._CalculationService__subscribed_affectors)
        # Restriction service
        for restriction in chain(
            fit._restriction._RestrictionService__rests,
            fit._restriction._RestrictionService__rest_regs_stateless,
            *fit._restriction._RestrictionService__rest_regs_stateful.values()
        ):
            entry_num += self._get_object_buffer_entry_amount(restriction)
        # Stats service
        for register in chain(
            fit.stats._StatService__regs_stateless,
            *fit.stats._StatService__regs_stateful.values()
        ):
            entry_num += self._get_object_buffer_entry_amount(register)
        # RAH simulator
        entry_num += self._get_object_buffer_entry_amount(fit._Fit__rah_sim)
        if entry_num > 0:
            plu = 'y' if entry_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(entry_num, plu)
            self.fail(msg=msg)

    def __clear_fit(self, fit):
        fit.ship = None
        fit.stance = None
        fit.character = None
        fit.effect_beacon = None
        fit.subsystems.clear()
        fit.modules.high.clear()
        fit.modules.med.clear()
        fit.modules.low.clear()
        fit.rigs.clear()
        fit.drones.clear()
        fit.skills.clear()
        fit.implants.clear()
        fit.boosters.clear()
