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


from eos.util.repr import make_repr_str


class WarfareBuffTemplate:

    def __init__(
        self,
        buff_id=None,
        affectee_filter=None,
        affectee_filter_extra_arg=None,
        affectee_attr_id=None,
        operator=None,
        aggregate_mode=None
    ):
        self.buff_id = buff_id
        self.affectee_filter = affectee_filter
        self.affectee_filter_extra_arg = affectee_filter_extra_arg
        self.affectee_attr_id = affectee_attr_id
        self.operator = operator
        self.aggregate_mode = aggregate_mode

    # Auxiliary methods
    def __repr__(self):
        spec = [
            'buff_id',
            'affectee_filter',
            'affectee_filter_extra_arg',
            'affectee_attr_id',
            'operator',
            'aggregate_mode']
        return make_repr_str(self, spec)
