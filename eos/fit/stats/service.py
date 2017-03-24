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


import math

from eos.const.eve import Attribute
from eos.fit.helper import DamageTypes, TankingLayers, TankingLayersTotal
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .container import *
from .register import *


class StatService(InheritableVolatileMixin):
    """
    Object which is used as access points for all
    fit statistics.

    Required arguments:
    fit -- Fit object to which service is assigned
    """

    def __init__(self, fit):
        InheritableVolatileMixin.__init__(self)
        self._fit = fit
        self._dd_reg = DamageDealerRegister(fit)
        # Initialize sub-containers
        self.cpu = ShipResource(fit, CpuUseRegister(fit), Attribute.cpu_output)
        self.powergrid = ShipResource(fit, PowerGridUseRegister(fit), Attribute.power_output)
        self.calibration = ShipResource(fit, CalibrationUseRegister(fit), Attribute.upgrade_capacity)
        self.dronebay = ShipResource(fit, DroneBayVolumeUseRegister(fit), Attribute.drone_capacity)
        self.drone_bandwidth = ShipResource(fit, DroneBandwidthUseRegister(fit), Attribute.drone_bandwidth)
        self.high_slots = ShipSlots(fit, fit.modules.high, Attribute.hi_slots)
        self.med_slots = ShipSlots(fit, fit.modules.med, Attribute.med_slots)
        self.low_slots = ShipSlots(fit, fit.modules.low, Attribute.low_slots)
        self.rig_slots = ShipSlots(fit, fit.rigs, Attribute.rig_slots)
        self.subsystem_slots = ShipSlots(fit, fit.subsystems, Attribute.max_subsystems)
        self.turret_slots = ShipSlots(fit, TurretUseRegister(fit), Attribute.turret_slots_left)
        self.launcher_slots = ShipSlots(fit, LauncherUseRegister(fit), Attribute.launcher_slots_left)
        self.launched_drones = CharSlots(fit, LaunchedDroneRegister(fit), Attribute.max_active_drones)
        self._volatile_containers = (
            self.cpu,
            self.powergrid,
            self.calibration,
            self.dronebay,
            self.drone_bandwidth,
            self.high_slots,
            self.med_slots,
            self.low_slots,
            self.rig_slots,
            self.subsystem_slots,
            self.turret_slots,
            self.launcher_slots,
            self.launched_drones
        )

    @volatile_property
    def hp(self):
        """
        Fetch current ship HP and return object with hull, armor, shield and
        total attributes. If fit has no ship or some data cannot be fetched,
        corresponding attribs will be set to None.
        """
        ship_item = self._fit.ship
        try:
            hp_data = ship_item.hp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)
        else:
            # Build tuple here because the object we fetched
            # from ship is access point to stats, which are
            # updated on fit changes
            return TankingLayersTotal(
                hull=hp_data.hull,
                armor=hp_data.armor,
                shield=hp_data.shield
            )

    @volatile_property
    def resistances(self):
        """
        Fetch current ship resistances and return object wit following data:
        .hull.em, .hull.thermal, .hull.kinetic, .hull.explosive,
        .armor.em, .armor.thermal, .armor.kinetic, .armor.explosive,
        .shield.em, .shield.thermal, .shield.kinetic, .shield.explosive
        If fit has no ship or some data cannot be fetched, corresponding attribs
            will be set to None.
        """
        ship_item = self._fit.ship
        try:
            return ship_item.resistances
        except AttributeError:
            empty = DamageTypes(em=None, thermal=None, kinetic=None, explosive=None)
            return TankingLayers(hull=empty, armor=empty, shield=empty)

    def get_ehp(self, damage_profile=None):
        """
        Same as hp, but takes damage_profile argument which optionally defines
        damage profile (should have em, thermal, kinetic and explosive arguments
        defined as numbers). Returns effective HP of a ship against this profile.
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None. If no profile is specified, default fit profile is
        taken.
        """
        ship_item = self._fit.ship
        try:
            return ship_item.get_ehp(damage_profile)
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    @volatile_property
    def worst_case_ehp(self):
        """
        Eve-style EHP for a ship - calculated using worst resistance for each layer.
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None.
        """
        ship_item = self._fit.ship
        try:
            return ship_item.worst_case_ehp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    def get_nominal_volley(self, item_filter=None, target_resistances=None):
        """
        Get nominal volley of whole fit.

        Optional arguments:
        item_filter -- when iterating over fit item, this function is called.
            If evaluated as True, this item is taken into consideration, else not.
            If argument is None, all items 'pass filter'. By default None.
        target_resistances -- resistance profile to calculate effective volley.
            Profile should contain em, thermal, kinetic and explosive attributes as
            numbers in range [0..1]. If None, 'raw' dps is calculated. By default None.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes.
        """
        volley = self._dd_reg._collect_damage_stats(
            item_filter,
            'get_nominal_volley',
            target_resistances=target_resistances
        )
        return volley

    def get_nominal_dps(self, item_filter=None, target_resistances=None, reload=False):
        """
        Get nominal dps of whole fit.

        Optional arguments:
        item_filter -- when iterating over fit item, this function is called.
            If evaluated as True, this item is taken into consideration, else not.
            If argument is None, all items 'pass filter'. By default None.
        target_resistances -- resistance profile to calculate effective dps.
            Profile should contain em, thermal, kinetic and explosive attributes as
            numbers in range [0..1]. If None, 'raw' dps is calculated. By default None.
        reload -- boolean flag, should reload be taken into consideration or not.
            By default False.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes.
        """
        dps = self._dd_reg._collect_damage_stats(
            item_filter,
            'get_nominal_dps',
            target_resistances=target_resistances,
            reload=reload
        )
        return dps

    @volatile_property
    def agility_factor(self):
        ship_item = self._fit.ship
        try:
            ship_attribs = ship_item.attributes
        except AttributeError:
            return None
        try:
            agility = ship_attribs[Attribute.agility]
            mass = ship_attribs[Attribute.mass]
        except KeyError:
            return None
        real_agility = -math.log(0.25) * agility * mass / 1000000
        return real_agility

    @volatile_property
    def align_time(self):
        try:
            return math.ceil(self.agility_factor)
        except TypeError:
            return None

    def _clear_volatile_attrs(self):
        """
        Clear volatile cache for self and all child objects.
        """
        for container in self._volatile_containers:
            container._clear_volatile_attrs()
        InheritableVolatileMixin._clear_volatile_attrs(self)
