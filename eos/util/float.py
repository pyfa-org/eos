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


"""
Sometimes use of floats may lead to undesirable results, e.g.

  int(2.3 / 0.1) = 22.

We cannot afford to use different number representations (e.g. representations
provided by decimal or fraction modules), thus consequences are worked around by
this module.
"""


import sys


# As we will be rounding numbers after operations (which introduce higher error
# than base float representation error), we need to keep less significant
# numbers than for single float number w/o operations
keep_digits = int(sys.float_info.dig / 2)


def float_to_int(value):
    """Convert number to integer, taking care of float errors."""
    return int(round(value, keep_digits))
