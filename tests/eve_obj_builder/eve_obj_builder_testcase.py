# ==============================================================================
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
# ==============================================================================


from eos.data.eve_obj_builder import EveObjBuilder
from eos.eve_object.modifier import DogmaModifier
from tests.eos_testcase import EosTestCase
from .environment import DataHandler


class EveObjBuilderTestCase(EosTestCase):
    """Class which should be used by eve object builder tests.

    Attributes:
        dh: Default data handler.
    """

    def setUp(self):
        EosTestCase.setUp(self)
        self.dh = DataHandler()

    def run_builder(self):
        """Shortcut to running eve object builder.

        Default data handler is passed to builder as data source, and results
        are and stored on test instance as following attributes:
            types: Map in {type ID: type} format.
            attrs: Map in {attribute ID: attribute} format.
            effects: Map in {effect ID: effect} format.
        """
        types, attrs, effects = EveObjBuilder.run(self.dh)
        self.types = {t.id: t for t in types}
        self.attrs = {a.id: a for a in attrs}
        self.effects = {e.id: e for e in effects}

    def mod(self, *args, **kwargs):
        """Shortcut to instantiating dogma modifier."""
        return DogmaModifier(*args, **kwargs)
