#===============================================================================
# Copyright (C) 2013 Anton Vorobyov
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


import json
import os.path

from .abc import DataHandler


class JsonDataHandler(DataHandler):
    """
    Implements loading of raw data from compressed JSON files produced by Phobos script, which can be found at
    http://fisheye.evefit.org/browse/phobos. Following command asks Phobos to gather all the data we need:
    python dumpToJson.py --eve=<eve path> --cache=<eve cache path> --tables=invtypes,invgroups,dgmtypeattribs,dgmattribs,dgmtypeeffects,dgmeffects,dgmexpressions --output=<output path>
    """

    def __init__(self, basepath):
        self.basepath = os.path.expanduser(basepath)

    def get_invtypes(self):
        return self.__fetch_file('invtypes')

    def get_invgroups(self):
        return self.__fetch_file('invgroups')

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

    def __fetch_file(self, filename):
        with open(os.path.join(self.basepath, '{}.json'.format(filename)), mode='r') as file:
            data = json.load(file)
        return data

    def get_version(self):
        metadata = self.__fetch_file('metadata')
        # If we won't find version field, it will be None
        version = None
        for row in metadata:
            if row['fieldName'] == 'clientBuild':
                version = row['fieldValue']
                break
        return version
