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


class CycleInfo:
    """Holds information about cycle sequence.

    This class is used only when all cycles in sequence have the same
    parameters.

    Args:
        time: Time between start of one cycle and start of next one.
        quantity: Defines how many times cycle should be repeated.
    """

    def __init__(self, time, quantity):
        self.time = time
        self.quantity = quantity


class CycleSequence:
    """Holds information about cycle sequence.

    This class can be used when cycles it describes have different parameters.

    Args:
        sequence: Container-sequence, which holds cycle sequence definition in
            the form of CycleSequence of CycleInfo instances.
        quantity: Defines how many times the sequence should be repeated.
    """

    def __init__(self, sequence, quantity):
        self.sequence = sequence
        self.quantity = quantity
