# ==============================================================================
# Copyright (C) 2013-2017 Anton Vorobyov
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


import json
import os
from collections.abc import Mapping

from eos.util.repr import make_repr_str
from .base import BaseDataHandler


class JsonDataHandler(BaseDataHandler):
    """JSON data handler implementation.

    Implements loading of raw data from JSON files produced by Phobos script,
    which can be found at https://github.com/pyfa-org/Phobos.

    Args:
        basepath: Path to folder with JSON files.
    """

    def __init__(self, basepath):
        self.basepath = os.path.abspath(basepath)

    def get_evetypes(self):
        return self.__fetch_file('fsd_lite', 'evetypes', values_only=True)

    def get_evegroups(self):
        return self.__fetch_file('fsd_lite', 'evegroups', values_only=True)

    def get_dgmattribs(self):
        return self.__fetch_file('fsd_binary', 'dogmaattributes', values_only=True)

    def get_dgmtypeattribs(self):
        rows = []
        for type_id, type_data in self.__fetch_file('fsd_binary', 'typedogma').items():
            type_id = int(type_id)
            for tdrow in type_data.get('dogmaAttributes', ()):
                rows.append({'typeID': type_id, 'attributeID': tdrow['attributeID'], 'value': tdrow['value']})
        return rows

    def get_dgmeffects(self):
        return self.__fetch_file('fsd_binary', 'dogmaeffects', values_only=True)

    def get_dgmtypeeffects(self):
        rows = []
        for type_id, type_data in self.__fetch_file('fsd_binary', 'typedogma').items():
            type_id = int(type_id)
            for tdrow in type_data.get('dogmaEffects', ()):
                rows.append({'typeID': type_id, 'effectID': tdrow['effectID'], 'isDefault': tdrow['isDefault']})
        return rows

    def get_dbuffcollections(self):
        rows = []
        dbuffs = self.__fetch_file('fsd_lite', 'dbuffcollections')
        for buff_id, row in dbuffs.items():
            row['buffID'] = int(buff_id)
            rows.append(row)
        return rows

    def get_typefighterabils(self):
        rows = []
        fighter_abils = self.__fetch_file('fsd_lite', 'fighterabilitiesbytype')
        for type_id, type_abilities in fighter_abils.items():
            for ability_slot, ability_data in type_abilities.items():
                ability_row = {'typeID': int(type_id)}
                self.__collapse_dict(ability_data, ability_row)
                rows.append(ability_row)
        return rows

    def __fetch_file(self, miner, filename, values_only=False):
        filepath = os.path.join(self.basepath, miner, '{}.json'.format(filename))
        with open(filepath, mode='r', encoding='utf8') as file:
            data = json.load(file)
        if values_only:
            data = list(data.values())
        return data

    def __collapse_dict(self, src, tgt):
        """Convert multi-level dictionary to single-level one."""
        for k, v in src.items():
            if isinstance(v, Mapping):
                self.__collapse_dict(v, tgt)
            elif k not in tgt:
                tgt[k] = v

    def get_version(self):
        metadata = self.__fetch_file('phobos', 'metadata')
        for row in metadata:
            if row['field_name'] == 'client_build':
                return row['field_value']
        else:
            return None

    def __repr__(self):
        spec = ['basepath']
        return make_repr_str(self, spec)
