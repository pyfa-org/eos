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

class Attribute:
    """Class-holder for attribute metadata"""

    def __init__(self, attrId, highIsGood=None, stackable=None):
        # Just ID of attribute, integer
        self.id = int(attrId) if attrId is not None else None

        # Boolean describing if it's good when attribute is high or not,
        # used in calculation process
        self.highIsGood = bool(highIsGood) if highIsGood is not None else None

        # Boolean which defines if attribute can be stacking penalized (False)
        # or not (True)
        self.stackable = bool(stackable) if stackable is not None else None
