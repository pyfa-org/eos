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


from eos.util.repr import make_repr_str


class CycleInfo:
    """Holds information about cycle sequence.

    This class is used only when all cycles in sequence have the same
    parameters.

    Attributes:
        active_time: How long this effect is active.
        inactive_time: How long this effect is inactive after its activity.
        quantity: Defines how many times cycle should be repeated.
    """

    def __init__(self, active_time, inactive_time, quantity):
        self.active_time = active_time
        self.inactive_time = inactive_time
        self.quantity = quantity

    @property
    def average_time(self):
        """Get average time between cycles."""
        return self.active_time + self.inactive_time

    def _get_cycle_quantity(self):
        return self.quantity

    def _get_time(self):
        return (self.active_time + self.inactive_time) * self.quantity

    def __repr__(self):
        spec = ['active_time', 'inactive_time', 'quantity']
        return make_repr_str(self, spec)


class CycleSequence:
    """Holds information about cycle sequence.

    This class can be used when cycles it describes have different parameters.

    Attributes:
        sequence: Container-sequence, which holds cycle sequence definition in
            the form of CycleSequence of CycleInfo instances.
        quantity: Defines how many times the sequence should be repeated.
    """

    def __init__(self, sequence, quantity):
        self.sequence = sequence
        self.quantity = quantity

    @property
    def average_time(self):
        """Get average time between cycles."""
        return self._get_time() / self._get_cycle_quantity()

    def _get_cycle_quantity(self):
        quantity = 0
        for item in self.sequence:
            quantity += item._get_cycle_quantity()
        return quantity

    def _get_time(self):
        time = 0
        for item in self.sequence:
            time += item._get_time()
        return time

    def __repr__(self):
        spec = ['sequence', 'quantity']
        return make_repr_str(self, spec)
