#===============================================================================
# Copyright (C) 2010-2011 Anton Vorobyov
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

# List of data types, sorted by ability to store data
type_BOOL = 1
type_INT = 2
type_FLOAT = 3
type_STR = 4
# In-EVE constants
group_EFFECTBEACON = 920
category_SHIP = 6
category_MODULE = 7
category_CHARGE = 8
category_SKILL = 16
category_DRONE = 18
category_IMPLANT = 20
category_SUBSYSTEM = 32
attribute_MASS = 4
attribute_CAPACITY = 38
attribute_VOLUME = 161
attribute_RADIUS = 162
attributeCategory_DEFATTR = 10  # Attributes assigned to this category are used to reference attribute by its value via ID
attributeCategory_DEFTYPE = 11  # Attributes assigned to this category are used to reference type by its value via ID
attributeCategory_DEFGROUP = 12  # Attributes assigned to this category are used to reference group by its value via ID
operand_DEFATTR = 22  # Operand which defines attribute
operand_DEFGRP = 26  # Operand which defines group
operand_DEFTYPE = 29  # Operand which defines type
