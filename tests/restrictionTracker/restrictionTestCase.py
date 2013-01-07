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


from eos.tests.eosTestCase import EosTestCase


class RestrictionTestCase(EosTestCase):
    """
    Special test case class, which should be used to test
    just restriction tracker and nothing else. Additional
    functionality provided:

    self.assertBuffersEmpty -- checks if restriction tracker
    buffers of passed fit are clear.
    """

    def assertBuffersEmpty(self, fit):
        entryNum = 0
        # Get dictionary-container with all registers used by tracker,
        # and cycle through all of them
        trackerContainer = fit._restrictionTracker._RestrictionTracker__registers
        for registerGroup in trackerContainer.values():
            for register in registerGroup:
                # Cycle through all attributes of each register, besides
                # __special__ ones, and add count their lengths as number
                # of detected entries
                for attrName in dir(register):
                    attrVal = getattr(register, attrName)
                    if attrName.startswith("__") and attrName.endswith("__"):
                        continue
                    try:
                        attrLen = len(attrVal)
                    except TypeError:
                        pass
                    else:
                        entryNum += attrLen
        # Raise error if we found any data in any register
        if entryNum > 0:
            plu = 'y' if entryNum == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(entryNum, plu)
            self.fail(msg=msg)
