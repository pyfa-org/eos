#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
#===============================================================================


from eos.exception import EosException


class RestrictionTrackerException(EosException):
    """All restriction tracker exceptions are based on this class."""
    pass


# Exceptions used by ResourceRegister subclasses
class CpuException(RestrictionTrackerException):
    """Raised when ship doesn't have enough CPU to fit all modules."""
    pass


class PowerGridException(RestrictionTrackerException):
    """Raised when ship doesn't have enough power grid to fit all modules."""
    pass


class CalibrationException(RestrictionTrackerException):
    """Raised when ship doesn't have enough calibration to fit all rigs."""
    pass


class DroneBayVolumeException(RestrictionTrackerException):
    """Raised when ship doesn't have enough drone bay volume to fit all drones."""
    pass


class DroneBandwidthException(RestrictionTrackerException):
    """Raised when ship doesn't have enough drone bandwidth to use all drones."""
    pass


# Exceptions used by SlotNumberRegister subclasses
class HighSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough high slots to fit all modules."""
    pass


class MediumSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough medium slots to fit all modules."""
    pass


class LowSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough medium slots to fit all modules."""
    pass


class RigSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough rig slots to fit all rigs."""
    pass


class SubsystemSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough subsystem slots to fit all subsystems."""
    pass


class TurretSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough turret hardpoints to fit all turrets."""
    pass


class LauncherSlotException(RestrictionTrackerException):
    """Raised when ship doesn't have enough launcher hardpoints to fit all missile launchers."""
    pass


# Exceptions used by SlotIndexRegister subclasses
class SubsystemIndexException(RestrictionTrackerException):
    """Raised when there're more than one subsystem fit to certain subsystem slot."""
    pass


class ImplantIndexException(RestrictionTrackerException):
    """Raised when there're more than one implant fit to certain implant slot."""
    pass


class BoosterIndexException(RestrictionTrackerException):
    """Raised when there're more than one booster fit to certain booster slot."""
    pass


# Exceptions used by MaxGroupRegister subclasses
class MaxGroupFittedException(RestrictionTrackerException):
    """Raised when excessive number of modules of certain group is fitted to ship."""
    pass


class MaxGroupOnlineException(RestrictionTrackerException):
    """Raised when excessive number of modules of certain group is online on ship."""
    pass


class MaxGroupActiveException(RestrictionTrackerException):
    """Raised when excessive number of modules of certain group is active on ship."""
    pass


class ShipTypeGroupException(RestrictionTrackerException):
    """Raised when item cannot be fitted to ship because of ship's type or group."""
    pass


class CapitalItemException(RestrictionTrackerException):
    """Raised when capital modules are fit on non-capital ship."""
    pass


class DroneGroupException(RestrictionTrackerException):
    """Raised when drones of certain group are put into drone bay of
    ship which doesn't allow it."""
    pass


class SkillRequirementException(RestrictionTrackerException):
    """Raised when any holder on fit has its skill requirements not satisfied."""
    pass
