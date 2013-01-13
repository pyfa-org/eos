#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


class DataHandler:

    def __init__(self):
        self.data = {'invtypes': [],
                     'invgroups': [],
                     'dgmattribs': [],
                     'dgmtypeattribs': [],
                     'dgmeffects': [],
                     'dgmtypeeffects': [],
                     'dgmexpressions': []}

    def getInvtypes(self):
        return self.data['invtypes']

    def getInvgroups(self):
        return self.data['invgroups']

    def getDgmattribs(self):
        return self.data['dgmattribs']

    def getDgmtypeattribs(self):
        return self.data['dgmtypeattribs']

    def getDgmeffects(self):
        return self.data['dgmeffects']

    def getDgmtypeeffects(self):
        return self.data['dgmtypeeffects']

    def getDgmexpressions(self):
        return self.data['dgmexpressions']
