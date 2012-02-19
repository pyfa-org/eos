#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.eve.attribute import Attribute
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.eosTestCase import EosTestCase


class TestNonExistent(EosTestCase):
    """Test return value when requesting attribute which isn't set"""

    def testAttributeAccess(self):
        attr = Attribute(1)
        fit = Fit({attr.id: attr})
        holder = IndependentItem(Type(None))
        fit._addHolder(holder)
        self.assertRaises(KeyError, holder.attributes.__getitem__, 1)


    def testDefaultValue(self):
        # Default value should be used if attribute
        # value is not available on item
        attr = Attribute(1, defaultValue=5.6)
        fit = Fit({attr.id: attr})
        holder = IndependentItem(Type(None))
        fit._addHolder(holder)
        self.assertAlmostEqual(holder.attributes[1], 5.6)
