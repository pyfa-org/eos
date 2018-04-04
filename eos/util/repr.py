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


def make_repr_str(instance, spec=None):
    """Prepare string for printing info about passed object.

    Args:
        instance: Object which we should get info from.
        spec (optional): Iterable which defines which fields we should include
            in info string. Each iterable element can be single attribute name,
            or tuple/list with two elements, where first defines reference name
            for info string, and second defines actual attribute name.

    Returns:
        String, which includes object's class name and requested additional
        fields.
    """
    arg_list = []
    for field in spec or ():
        if isinstance(field, str):
            repr_name, attr_name = field, field
        else:
            repr_name, attr_name = field
        attr_val = getattr(instance, attr_name, 'N/A')
        arg_list.append('{}={}'.format(repr_name, attr_val))
    return '<{}({})>'.format(type(instance).__name__, ', '.join(arg_list))
