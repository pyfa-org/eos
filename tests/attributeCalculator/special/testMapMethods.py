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


class TestMapMethods(AttrCalcTestCase):
    """Test map methods not covered by other test cases"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.attr1 = Attribute(1)
        self.attr2 = Attribute(2)
        self.attr3 = Attribute(3)
        self.fit = Fit({self.attr1.id: self.attr1, self.attr2.id: self.attr2, self.attr3.id: self.attr3})
        self.holder = IndependentItem(Type(None, attributes={self.attr1.id: 5, self.attr2.id: 10}))
        self.fit.items.append(self.holder)
        self.holder.attributes._MutableAttributeMap__modifiedAttributes = {self.attr2.id: 20, self.attr3.id: 40}

    def testLen(self):
        # Length should return length, counting unique
        # IDs from both attribute containers
        self.assertEqual(len(self.holder.attributes), 3)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testContains(self):
        # Make sure map reacts positively to holders contained
        # in any attribute container, and negatively for attributes
        # which were not found
        self.assertTrue(self.attr1.id in self.holder.attributes)
        self.assertTrue(self.attr2.id in self.holder.attributes)
        self.assertTrue(self.attr3.id in self.holder.attributes)
        self.assertFalse(1008 in self.holder.attributes)
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testKeys(self):
        # When we request map keys, they should include all unique
        # attribute IDs w/o duplication
        self.assertCountEqual(self.holder.attributes.keys(), (self.attr1.id, self.attr2.id, self.attr3.id))
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)

    def testIter(self):
        # Iter should return the same keys as keys(). CountEqual
        # takes any iterable - we just check its contents here,
        # w/o checking format of returned data
        self.assertCountEqual(self.holder.attributes, (self.attr1.id, self.attr2.id, self.attr3.id))
        self.fit.items.remove(self.holder)
        self.assertBuffersEmpty(self.fit)
