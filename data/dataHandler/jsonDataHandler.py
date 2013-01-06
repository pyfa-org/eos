#===============================================================================
# Copyright (C) 2012 Anton Vorobyov
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

from .dataHandler import DataHandler


class JsonDataHandler(DataHandler):
    """
    Implements loading of raw data from compressed JSON
    files produced by Phobos script, which can be found at
    http://fisheye.evefit.org/browse/phobos
    """

    def __init__(self, basepath):
        self.basepath = os.path.expanduser(basepath)

    def getInvtypes(self):
        return self.__fetchFile('invtypes')

    def getInvgroups(self):
        return self.__fetchFile('invgroups')

    def getDgmattribs(self):
        return self.__fetchFile('dgmattribs')

    def getDgmtypeattribs(self):
        return self.__fetchFile('dgmtypeattribs')

    def getDgmeffects(self):
        return self.__fetchFile('dgmeffects')

    def getDgmtypeeffects(self):
        return self.__fetchFile('dgmtypeeffects')

    def getDgmexpressions(self):
        return self.__fetchFile('dgmexpressions')

    def __fetchFile(self, filename):
        with open(os.path.join(self.basepath, '{}.json'.format(filename)), mode='r') as file:
            data = json.load(file)
        return data

    def getVersion(self):
        # If no version file is found, return None
        try:
            version = self.__fetchFile('version')
        except IOError:
            version = None
        return version
