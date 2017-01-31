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


from contextlib import ExitStack
from unittest.mock import patch

from eos.fit.fit import Fit as FitBase
from eos.util.volatile_cache import InheritableVolatileMixin


class Item:

    def __init__(self):
        self._fit = None


class Fit(FitBase):

    def __init__(self, source=None, message_assertions=None):
        self._message_assertions = message_assertions
        self.assertions_enabled = False
        self.message_store = []
        ctx_managers = (
            patch('eos.fit.fit.CalculationService'),
            patch('eos.fit.fit.RestrictionService'),
            patch('eos.fit.fit.StatService', spec=InheritableVolatileMixin)
        )
        with ExitStack() as stack:
            for mgr in ctx_managers:
                stack.enter_context(mgr)
            FitBase.__init__(self, source=source)
        self.character = None

    def _publish(self, message):
        if self._message_assertions is not None and self.assertions_enabled is True:
            try:
                assertion = self._message_assertions[type(message)]
            except KeyError:
                pass
            else:
                assertion(self)
        self.message_store.append(message)
        FitBase._publish(self, message)


class FitAssertion:

    def __init__(self, fit):
        self.fit = fit

    def __enter__(self):
        self.fit.assertions_enabled = True

    def __exit__(self, *args):
        self.fit.assertions_enabled = False
