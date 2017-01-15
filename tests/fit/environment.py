# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from unittest.mock import patch, DEFAULT

from eos.fit import Fit


class Holder:

    def __init__(self):
        self._fit = None

class TestFit(Fit):

    def __init__(self, source=None, message_assertions=None):
        self._message_assertions = message_assertions
        self.check_assertions = False
        self.message_store = []
        with patch.multiple('eos.fit.fit',
                CalculationService=DEFAULT,
                RestrictionService=DEFAULT,
                StatService=DEFAULT
        ):
            Fit.__init__(self, source=source)
        self.character = None

    def _publish(self, message):
        if self._message_assertions is not None and self.check_assertions is True:
            try:
                assertion = self._message_assertions[type(message)]
            except KeyError:
                pass
            else:
                assertion(self)
        self.message_store.append(message)
        Fit._publish(self, message)


class FitAssertionChecks:

    def __init__(self, fit):
        self.fit = fit

    def __enter__(self):
        self.fit.check_assertions = True

    def __exit__(self, *args):
        self.fit.check_assertions = False
