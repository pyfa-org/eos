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
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.environment import Logger


class TestNonExistent(AttrCalcTestCase):
    """Test return value when requesting attribute which isn't set"""

    def testAttributeError(self):
        # Check case when attribute value is available, but
        # data handler doesn't know about such attribute
        fit = Fit({})
        holder = IndependentItem(Type(57, attributes={105: 20}))
        fit._addHolder(holder)
        self.assertRaises(KeyError, holder.attributes.__getitem__, 105)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.attributeCalculator")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "unable to fetch metadata for attribute 105, requested for item 57")
        fit._removeHolder(holder)
        self.assertBuffersEmpty(fit)

    def testBaseValueError(self):
        # Check case when default value of attribute cannot be
        # determined. and item itself doesn't define any value
        # either
        attr = Attribute(89)
        fit = Fit({attr.id: attr})
        holder = IndependentItem(Type(649))
        fit._addHolder(holder)
        self.assertRaises(KeyError, holder.attributes.__getitem__, 89)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.attributeCalculator")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "unable to find base value for attribute 89 on item 649")
        fit._removeHolder(holder)
        self.assertBuffersEmpty(fit)


    def testDefaultValue(self):
        # Default value should be used if attribute
        # value is not available on item
        attr = Attribute(1, defaultValue=5.6)
        fit = Fit({attr.id: attr})
        holder = IndependentItem(Type(None))
        fit._addHolder(holder)
        self.assertAlmostEqual(holder.attributes[1], 5.6)
        fit._removeHolder(holder)
        self.assertBuffersEmpty(fit)
