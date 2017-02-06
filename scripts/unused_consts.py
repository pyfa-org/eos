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


"""Find all defined constants which are not actually used in eos code"""


import os
import sys


script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(script_dir, '..')))


from enum import IntEnum

import eos.const.eos
import eos.const.eve


enums = []


for module in (eos.const.eos, eos.const.eve):
    for item in module.__dict__.values():
        try:
            if issubclass(item, IntEnum) and item is not IntEnum:
                enums.append(item)
        # Not all of module level items are classes
        except TypeError:
            continue


