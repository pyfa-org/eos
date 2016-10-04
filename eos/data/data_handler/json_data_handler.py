# ===============================================================================
# Copyright (C) 2013-2015 Anton Vorobyov
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


import json
import os.path

from eos.util.repr import make_repr_str
from .abc import BaseDataHandler


class JsonDataHandler(BaseDataHandler):
    """
    Implements loading of raw data from JSON files produced by Phobos script, which can be found at
    https://github.com/pyfa-org/Phobos.
    """

    def __init__(self, basepath):
        self.basepath = basepath

    def get_evetypes(self):
        return self.__fetch_file('evetypes', values_only=True)

    def get_evegroups(self):
        return self.__fetch_file('evegroups', values_only=True)

    def get_dgmattribs(self):
        return self.__fetch_file('dgmattribs')

    def get_dgmtypeattribs(self):
        return self.__fetch_file('dgmtypeattribs')

    def get_dgmeffects(self):
        return self.__fetch_file('dgmeffects')

    def get_dgmtypeeffects(self):
        return self.__fetch_file('dgmtypeeffects')

    def get_dgmexpressions(self):
        return self.__fetch_file('dgmexpressions')

    def __fetch_file(self, filename, values_only=False):
        with open(os.path.join(self.basepath, '{}.json'.format(filename)), mode='r', encoding='utf8') as file:
            data = json.load(file)
        if values_only:
            data = list(data.values())
        return data

    def get_version(self):
        metadata = self.__fetch_file('phbmetadata')
        for row in metadata:
            if row['field_name'] == 'client_build':
                return row['field_value']
        else:
            return None

    def __repr__(self):
        spec = ['basepath']
        return make_repr_str(self, spec)
