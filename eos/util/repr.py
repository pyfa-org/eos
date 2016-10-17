# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


def make_repr_str(instance, spec):
    """
    Return single string which includes object class name and
    attribute names/values from spec.

    Required arguments:
    instance -- instance for which line will be built
    spec -- specification of what to print in (field spec), ...) format,
    where field spec is (representative name, attribute name) tuple
    if those two differ, or simply string if they match.
    """
    arg_list = []
    for field in spec:
        if isinstance(field, str):
            repr_name, attr_name = field, field
        else:
            repr_name, attr_name = field
        attr_val = getattr(instance, attr_name)
        arg_list.append('{}={}'.format(repr_name, attr_val))
    return '<{}({})>'.format(type(instance).__name__, ', '.join(arg_list))
