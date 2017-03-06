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


from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestMapMethods(CalculatorTestCase):
    """Test map methods not covered by other test cases"""

    def setUp(self):
        super().setUp()
        self.attr1 = self.ch.attribute()
        self.attr2 = self.ch.attribute()
        self.attr3 = self.ch.attribute()
        self.item = IndependentItem(self.ch.type(attributes={self.attr1.id: 5, self.attr2.id: 10}))
        self.fit.items.add(self.item)
        self.item.attributes._MutableAttributeMap__modified_attributes = {self.attr2.id: 20, self.attr3.id: 40}

    def test_get(self):
        # Make sure map's get method replicates functionality
        # of dictionary get method
        self.assertEqual(self.item.attributes.get(self.attr1.id), 5)
        self.assertEqual(self.item.attributes.get(self.attr2.id), 20)
        self.assertEqual(self.item.attributes.get(self.attr3.id), 40)
        self.assertIsNone(self.item.attributes.get(1008))
        self.assertEqual(self.item.attributes.get(1008, 60), 60)
        self.fit.items.remove(self.item)
        # Attempt to fetch non-existent attribute generates
        # error, which is not related to this test
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(self.fit)

    def test_len(self):
        # Length should return length, counting unique
        # IDs from both attribute containers
        self.assertEqual(len(self.item.attributes), 3)
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_contains(self):
        # Make sure map reacts positively to items contained
        # in any attribute container, and negatively for attributes
        # which were not found
        self.assertTrue(self.attr1.id in self.item.attributes)
        self.assertTrue(self.attr2.id in self.item.attributes)
        self.assertTrue(self.attr3.id in self.item.attributes)
        self.assertFalse(1008 in self.item.attributes)
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_keys(self):
        # When we request map keys, they should include all unique
        # attribute IDs w/o duplication
        self.assertCountEqual(self.item.attributes.keys(), (self.attr1.id, self.attr2.id, self.attr3.id))
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_iter(self):
        # Iter should return the same keys as keys(). CountEqual
        # takes any iterable - we just check its contents here,
        # w/o checking format of returned data
        self.assertCountEqual(self.item.attributes, (self.attr1.id, self.attr2.id, self.attr3.id))
        self.fit.items.remove(self.item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
