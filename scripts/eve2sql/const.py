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


class DataType(object):
    """List of data types"""
    # Values must be ascending, sorted by ability to store data
    # (e.g. float can store integer, str can store float, etc.)
    boolean = 1
    integer = 2
    float_ = 3
    string = 4


class Type(object):
    """EVE items"""
    character_static = 1381


class Group(object):
    """EVE item groups"""
    effect_beacon = 920


class Category(object):
    """EVE item categories"""
    ship = 6
    module = 7
    charge = 8
    skill = 16
    drone = 18
    implant = 20
    subsystem = 32


class Attribute(object):
    """EVE attributes"""
    mass = 4
    capacity = 38
    volume = 161
    radius = 162


class AttributeCategory(object):
    """EVE attribute categories"""
    define_attribute = 10  # Attributes assigned to this category are used to reference attribute by its value via ID
    define_type = 11  # Attributes assigned to this category are used to reference type by its value via ID
    define_group = 12  # Attributes assigned to this category are used to reference group by its value via ID


class Effect(object):
    """EVE effects"""
    low_power = 11
    high_power = 12
    medium_power = 13


class Operand(object):
    """EVE expression operands"""
    define_attribute = 22  # Operand which defines attribute
    define_group = 26  # Operand which defines group
    define_type = 29  # Operand which defines type
