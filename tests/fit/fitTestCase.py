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


from unittest.mock import patch

from eos.tests.eosTestCase import EosTestCase


class FitTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assertObjectBuffersEmpty -- checks if fit has
    any holders assigned to it. By default ignores
    character holder because it's set by fit automatically.
    """

    def assertFitBuffersEmpty(self, fit, ignoreCharacter=True):
        holderNum = 0
        ignoredHolders = set()
        # Check if we have anything in our single holder  storages
        singleHolders = ('character', 'ship', 'systemWide')
        for attrName in singleHolders:
            holder = getattr(fit, attrName, None)
            if holder is not None:
                if ignoreCharacter and attrName == 'character':
                    ignoredHolders.add(holder)
                else:
                    holderNum += 1
        # Seek for multiple holder storages
        for attrName in dir(fit):
            if attrName.startswith("__") and attrName.endswith("__"):
                continue
            buffer = getattr(fit, attrName)
            if hasattr(buffer, '__iter__'):
                for holder in buffer:
                    if holder not in ignoredHolders:
                        holderNum += 1
        if holderNum > 0:
            plu = 'y' if holderNum == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(holderNum, plu)
            self.fail(msg=msg)
