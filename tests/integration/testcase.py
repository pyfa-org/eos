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


from copy import copy

from eos.const.eve import AttrId
from eos.item import Skill
from eos.eve_obj.modifier import DogmaModifier
from eos.source import Source
from eos.source import SourceManager
from tests.testcase import EosTestCase
from .environment import CacheHandler


class IntegrationTestCase(EosTestCase):
    """Test case class is used by integration tests.

    Supports almost end-to-end testing of Eos, leaving only data handler, cache
    handler and eve object builder outside of scope.

    Sets up two sources for fit, src1 (default) and src2.
    """

    def setUp(self):
        EosTestCase.setUp(self)
        # Replace existing sources with test source
        self.__backup_sources = copy(SourceManager._sources)
        self.__backup_default_source = SourceManager.default
        SourceManager._sources.clear()
        self._make_source('src1', CacheHandler(), make_default=True)

    def tearDown(self):
        # Revert source change
        SourceManager._sources.clear()
        SourceManager._sources.update(self.__backup_sources)
        SourceManager.default = self.__backup_default_source
        EosTestCase.tearDown(self)

    def _make_source(self, alias, cache_handler, make_default=False):
        source = Source(alias, cache_handler)
        # Add source 'manually' to avoid building cache
        SourceManager._sources[alias] = source
        if make_default is True:
            SourceManager.default = source
        return source

    def mktype(self, *args, src=None, **kwargs):
        """Make item type and add it to source.

        Args:
            src (optional): Source alias to which type should be added. Default
                source is used by default.
            *args: Arguments which will be used to instantiate item type.
            **kwargs: Keyword arguments which will be used to instantiate item
                type.

        Returns:
            Item type.
        """
        if src is None:
            src = SourceManager.default
        else:
            src = SourceManager.get(src)
        return src.cache_handler.mktype(*args, **kwargs)

    def mkattr(self, *args, src=None, **kwargs):
        """Make attribute and add it to default source.

        Args:
            src (optional): Source alias to which attribute should be added.
                Default source is used by default.
            *args: Arguments which will be used to instantiate attribute.
            **kwargs: Keyword arguments which will be used to instantiate
                attribute.

        Returns:
            Attribute.
        """
        if src is None:
            src = SourceManager.default
        else:
            src = SourceManager.get(src)
        return src.cache_handler.mkattr(*args, **kwargs)

    def mkeffect(self, *args, src=None, **kwargs):
        """Make effect and add it to default source.

        Args:
            src (optional): Source alias to which effect should be added.
                Default source is used by default.
            *args: Arguments which will be used to instantiate effect.
            **kwargs: Keyword arguments which will be used to instantiate
                effect.

        Returns:
            Effect.
        """
        if src is None:
            src = SourceManager.default
        else:
            src = SourceManager.get(src)
        return src.cache_handler.mkeffect(*args, **kwargs)

    def mkmod(self, *args, **kwargs):
        """Shortcut to instantiating dogma modifier.

        Args:
            *args: Arguments which will be used to instantiate modifier.
            **kwargs: Keyword arguments which will be used to instantiate
                modifier.

        Returns:
            Dogma modifier.
        """
        return DogmaModifier(*args, **kwargs)

    def allocate_type_id(self, *srcs):
        """Allocate item type ID which is not taken in specified sources.

        Args:
            *srcs: List of source aliases.

        Returns:
            Allocated item type ID.
        """
        if not srcs:
            srcs = [SourceManager.default.alias]
        return max(
            SourceManager.get(src).cache_handler.allocate_type_id()
            for src in srcs)

    def allocate_attr_id(self, *srcs):
        """Allocate attribute ID which is not taken in specified sources.

        Args:
            *srcs: List of source aliases.

        Returns:
            Allocated attribute ID.
        """
        if not srcs:
            srcs = [SourceManager.default.alias]
        return max(
            SourceManager.get(src).cache_handler.allocate_attr_id()
            for src in srcs)

    def allocate_effect_id(self, *srcs):
        """Allocate effect ID which is not taken in specified sources.

        Args:
            *srcs: List of source aliases.

        Returns:
            Allocated effect ID.
        """
        if not srcs:
            srcs = [SourceManager.default.alias]
        return max(
            SourceManager.get(src).cache_handler.allocate_effect_id()
            for src in srcs)

    def assert_solsys_buffers_empty(self, solsys):
        """Verify if solar system contains anything in object containers.

        Only containers which are designed to hold temporary data are verified.
        Verifies fits too, after removing them from solar system.

        Args:
            solsys: Solar system to verify.
        """
        # Clear
        solsys_fits = set(solsys.fits)
        solsys.fits.clear()
        # Verify
        entry_num = self._get_obj_buffer_entry_count(
            solsys,
            ignore_attrs=(('SolarSystem', '_SolarSystem__source'),))
        # Report
        if entry_num:
            msg = (
                '{} entries in solar system buffers: '
                'buffers must be empty').format(entry_num)
            self.fail(msg=msg)
        # Verify child objects
        for solsys_fit in solsys_fits:
            self.assert_fit_buffers_empty(solsys_fit)

    def assert_fit_buffers_empty(self, fit):
        """Checks if fit contains anything in object containers.

        Only containers which are designed to hold temporary data are checked.
        Verifies items too, after removing them from fit.

        Args:
            fit: Fit to verify.
        """

        def clear_fit(fit):
            # Container for items stored on fit - i.e. not including stuff like
            # charges, as they will still be connected to their parent item and
            # verified via it
            top_level_items = set()
            single_names = (
                'character',
                'ship',
                'stance',
                'effect_beacon')
            for container_name in single_names:
                item = getattr(fit, container_name)
                if item is not None:
                    top_level_items.add(item)
                    setattr(fit, container_name, None)
            ordered = (
                fit.modules.high,
                fit.modules.mid,
                fit.modules.low)
            for container in ordered:
                if len(container.items()) == 0:
                    continue
                for item in container.items():
                    top_level_items.add(item)
                container.clear()
            unordered = (
                fit.subsystems,
                fit.rigs,
                fit.drones,
                fit.fighters,
                fit.skills,
                fit.implants,
                fit.boosters)
            for container in unordered:
                if len(container) == 0:
                    continue
                for item in container:
                    top_level_items.add(item)
                container.clear()
            return top_level_items

        # Clear
        fit_items = clear_fit(fit)
        # Verify
        entry_num = self._get_obj_buffer_entry_count(
            fit,
            ignore_attrs=(
                # Disallow to investigate parent
                ('Fit', 'solar_system'),
                # Allowed to always reside on fit
                ('Fit', '_Fit__incoming_dmg_default'),
                # Allowed to always reside on fit
                ('Fit', '_Fit__incoming_dmg_rah'),
                # Restriction registers are always in subscribers
                ('Fit', '_FitMsgBroker__subscribers'),
                # Service is allowed to keep list of restrictions permanently
                ('RestrictionService', '_RestrictionService__restrictions')))
        # Report
        if entry_num:
            msg = '{} entries in fit buffers: buffers must be empty'.format(
                entry_num)
            self.fail(msg=msg)
        # Verify child objects
        for fit_item in fit_items:
            self.assert_item_buffers_empty(fit_item)

    def assert_item_buffers_empty(self, item):
        """Checks if item contains anything in object containers.

        Only containers which are designed to hold temporary data are checked.

        Args:
            item: Item to verify.
        """
        # Clear
        if isinstance(item, Skill):
            item.attrs._del_override_callback(AttrId.skill_level)
        # Verify
        entry_num = self._get_obj_buffer_entry_count(
            item,
            ignore_attrs=(
                # Disallow to investigate parent
                ('BaseItemMixin', '_container'),
                # Allowed to carry effect settings permanently
                ('BaseItemMixin', '_BaseItemMixin__effect_mode_overrides')))
        # Report
        if entry_num:
            msg = '{} entries in item buffers: buffers must be empty'.format(
                entry_num)
            self.fail(msg=msg)
