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


class Column(object):
    """
    Class-container for column data
    """
    def __init__(self, name):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "datatype", None)
        object.__setattr__(self, "datalen", None)
        object.__setattr__(self, "notnull", None)
        object.__setattr__(self, "unique", None)
        object.__setattr__(self, "pk", None)
        object.__setattr__(self, "fk", None)
        object.__setattr__(self, "index", None)

    def __setattr__(self, name, value):
        try:
            getattr(self, name)
        except AttributeError:
            raise ValueError("setting of new attributes prohibited")
        object.__setattr__(self, name, value)
