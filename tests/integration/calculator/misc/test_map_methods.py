# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from eos import Implant
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestMapMethods(CalculatorTestCase):
    """Test map methods not covered by other test cases."""

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.attr1 = self.mkattr()
        self.attr2 = self.mkattr()
        self.attr3 = self.mkattr(default_value=11)
        self.attr4 = self.mkattr()
        self.attr5 = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr1.id,
            operator=ModOperator.post_mul,
            src_attr_id=self.attr5.id)
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr2.id,
            operator=ModOperator.post_mul,
            src_attr_id=self.attr5.id)
        modifier3 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr3.id,
            operator=ModOperator.post_mul,
            src_attr_id=self.attr5.id)
        modifier4 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr4.id,
            operator=ModOperator.post_mul,
            src_attr_id=self.attr5.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=(modifier1, modifier2, modifier3, modifier4))
        self.item = Implant(self.mktype(
            attrs={self.attr1.id: 5, self.attr2.id: 10, self.attr5.id: 4},
            effects=[effect]).id)
        self.fit.implants.add(self.item)

    def calculate_attrs(self, special=()):
        for attr in (
                self.attr1.id, self.attr2.id, self.attr3.id, self.attr4.id,
                self.attr5.id, *special):
            self.item.attrs.get(attr)

    def test_getattr(self):
        self.assertAlmostEqual(self.item.attrs[self.attr1.id], 20)
        self.assertAlmostEqual(self.item.attrs[self.attr2.id], 40)
        self.assertAlmostEqual(self.item.attrs[self.attr3.id], 44)
        with self.assertRaises(KeyError):
            self.item.attrs[self.attr4.id]
        self.assertAlmostEqual(self.item.attrs[self.attr5.id], 4)
        with self.assertRaises(KeyError):
            self.item.attrs[1008]
        self.assert_fit_buffers_empty(self.fit)
        # Attempts to fetch non-existent attribute and attribute without base
        # value generate errors, which is not related to this test
        self.assertEqual(len(self.get_log()), 2)

    def test_getattr_not_loaded(self):
        self.fit.solar_system.source = None
        with self.assertRaises(KeyError):
            self.item.attrs[self.attr1.id]
        with self.assertRaises(KeyError):
            self.item.attrs[self.attr2.id]
        with self.assertRaises(KeyError):
            self.item.attrs[self.attr3.id]
        with self.assertRaises(KeyError):
            self.item.attrs[self.attr4.id]
        with self.assertRaises(KeyError):
            self.item.attrs[self.attr5.id]
        with self.assertRaises(KeyError):
            self.item.attrs[1008]
        self.assert_fit_buffers_empty(self.fit)
        # Attempts to fetch non-existent attribute and attribute without base
        # value generate errors, which is not related to this test
        self.assertEqual(len(self.get_log()), 6)

    def test_get(self):
        # Make sure map's get method replicates functionality of dictionary get
        # method
        self.assertAlmostEqual(self.item.attrs.get(self.attr1.id), 20)
        self.assertAlmostEqual(self.item.attrs.get(self.attr2.id), 40)
        self.assertAlmostEqual(self.item.attrs.get(self.attr3.id), 44)
        self.assertIsNone(self.item.attrs.get(self.attr4.id))
        self.assertAlmostEqual(self.item.attrs.get(self.attr5.id), 4)
        self.assertIsNone(self.item.attrs.get(1008))
        self.assertEqual(self.item.attrs.get(1008, 60), 60)
        self.assert_fit_buffers_empty(self.fit)
        # Attempts to fetch non-existent attribute and attribute without base
        # value generate errors, which is not related to this test
        self.assertEqual(len(self.get_log()), 3)

    def test_get_not_loaded(self):
        self.fit.solar_system.source = None
        self.assertIsNone(self.item.attrs.get(self.attr1.id))
        self.assertIsNone(self.item.attrs.get(self.attr2.id))
        self.assertIsNone(self.item.attrs.get(self.attr3.id))
        self.assertIsNone(self.item.attrs.get(self.attr4.id))
        self.assertIsNone(self.item.attrs.get(self.attr5.id))
        self.assertIsNone(self.item.attrs.get(1008))
        self.assertEqual(self.item.attrs.get(1008, 60), 60)
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 7)

    def test_len(self):
        # Length should return length, counting unique IDs from both attribute
        # containers. First, values are not calculated
        self.assertEqual(len(self.item.attrs), 3)
        # Force calculation
        self.calculate_attrs(special=[1008])
        # Length should change, as it now includes attribute which had no value
        # on item but has default value
        self.assertEqual(len(self.item.attrs), 4)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        # Log entries are unrelated to this test
        self.assertEqual(len(self.get_log()), 2)

    def test_len_not_loaded(self):
        self.fit.solar_system.source = None
        self.assertEqual(len(self.item.attrs), 0)
        self.calculate_attrs(special=[1008])
        self.assertEqual(len(self.item.attrs), 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 6)

    def test_contains(self):
        # Make sure map reacts positively to items contained in any attribute
        # container, and negatively for attributes which were not found
        self.assertTrue(self.attr1.id in self.item.attrs)
        self.assertTrue(self.attr2.id in self.item.attrs)
        self.assertFalse(self.attr3.id in self.item.attrs)
        self.assertFalse(self.attr4.id in self.item.attrs)
        self.assertTrue(self.attr5.id in self.item.attrs)
        self.assertFalse(1008 in self.item.attrs)
        self.calculate_attrs(special=[1008])
        self.assertTrue(self.attr1.id in self.item.attrs)
        self.assertTrue(self.attr2.id in self.item.attrs)
        self.assertTrue(self.attr3.id in self.item.attrs)
        self.assertFalse(self.attr4.id in self.item.attrs)
        self.assertTrue(self.attr5.id in self.item.attrs)
        self.assertFalse(1008 in self.item.attrs)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        # Log entries are unrelated to this test
        self.assertEqual(len(self.get_log()), 2)

    def test_contains_not_loaded(self):
        self.fit.solar_system.source = None
        self.assertFalse(self.attr1.id in self.item.attrs)
        self.assertFalse(self.attr2.id in self.item.attrs)
        self.assertFalse(self.attr3.id in self.item.attrs)
        self.assertFalse(self.attr4.id in self.item.attrs)
        self.assertFalse(self.attr5.id in self.item.attrs)
        self.assertFalse(1008 in self.item.attrs)
        self.calculate_attrs(special=[1008])
        self.assertFalse(self.attr1.id in self.item.attrs)
        self.assertFalse(self.attr2.id in self.item.attrs)
        self.assertFalse(self.attr3.id in self.item.attrs)
        self.assertFalse(self.attr4.id in self.item.attrs)
        self.assertFalse(self.attr5.id in self.item.attrs)
        self.assertFalse(1008 in self.item.attrs)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 6)

    def test_keys(self):
        # When we request map keys, they should include all unique attribute IDs
        # w/o duplication
        self.assertCountEqual(
            self.item.attrs.keys(),
            (self.attr1.id, self.attr2.id, self.attr5.id))
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(
            self.item.attrs.keys(),
            (self.attr1.id, self.attr2.id, self.attr3.id, self.attr5.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        # Log entries are unrelated to this test
        self.assertEqual(len(self.get_log()), 2)

    def test_keys_not_loaded(self):
        self.fit.solar_system.source = None
        self.assertCountEqual(self.item.attrs.keys(), ())
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(self.item.attrs.keys(), ())
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 6)

    def test_items(self):
        # As with keys, we include unique attribute IDs, plus their calculated
        # values
        self.assertCountEqual(
            self.item.attrs.items(),
            ((self.attr1.id, 20), (self.attr2.id, 40), (self.attr5.id, 4)))
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(
            self.item.attrs.items(), (
                (self.attr1.id, 20), (self.attr2.id, 40),
                (self.attr3.id, 44), (self.attr5.id, 4)))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        # Log entries are unrelated to this test
        self.assertEqual(len(self.get_log()), 2)

    def test_items_not_loaded(self):
        self.fit.solar_system.source = None
        self.assertCountEqual(self.item.attrs.items(), ())
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(self.item.attrs.items(), ())
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        # Log entries are unrelated to this test
        self.assertEqual(len(self.get_log()), 6)

    def test_iter(self):
        # Iter should return the same keys as keys(). CountEqual takes any
        # iterable - we just check its contents here, w/o checking format of
        # returned data
        self.assertCountEqual(
            self.item.attrs, (self.attr1.id, self.attr2.id, self.attr5.id))
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(
            self.item.attrs,
            (self.attr1.id, self.attr2.id, self.attr3.id, self.attr5.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        # Log entries are unrelated to this test
        self.assertEqual(len(self.get_log()), 2)

    def test_iter_not_loaded(self):
        self.fit.solar_system.source = None
        self.assertCountEqual(self.item.attrs, ())
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(self.item.attrs, ())
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 6)
