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


from unittest.mock import Mock

from eos.const.eos import Restriction, State
from eos.fit.restrictionTracker import RestrictionTracker, ValidationError
from eos.tests.eosTestCase import EosTestCase


class RestrictionTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.rt -- restriction tracker instance for tests
    self.setShip -- set ship to fit which uses self.rt
    self.setCharacter -- set character to fit whic uses
    self.rt
    self.trackHolder -- add holder to restriction tracker
    self.untrackHolder -- remove holder from restriction
    tracker
    self.getRestrictionError -- get restriction error for
    passed holder of passed restriction type. If no error
    occurred, return None
    self.assertRestrictionBuffersEmpty -- checks if
    restriction tracker buffers are clear
    """

    def setUp(self):
        EosTestCase.setUp(self)
        fit = Mock()
        fit.ship = None
        fit.character = None
        self.rt = RestrictionTracker(fit)

    def setShip(self, holder):
        self.rt._fit.ship = holder

    def setCharacter(self, holder):
        self.rt._fit.character = holder

    def trackHolder(self, holder):
        self.rt.enableStates(holder, set(filter(lambda s: s <= holder.state, State)))

    def untrackHolder(self, holder):
        self.rt.disableStates(holder, set(filter(lambda s: s <= holder.state, State)))

    def getRestrictionError(self, holder, restriction):
        skipChecks = set(Restriction).difference((restriction,))
        try:
            self.rt.validate(skipChecks)
        except ValidationError as e:
            errorData = e.args[0]
            if holder not in errorData:
                return None
            holderError = errorData[holder]
            if restriction not in holderError:
                return None
            return holderError[restriction]
        else:
            return None

    def assertRestrictionBuffersEmpty(self):
        entryNum = 0
        # Get dictionary-container with all registers used by tracker,
        # and cycle through all of them
        trackerContainer = self.rt._RestrictionTracker__registers
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
