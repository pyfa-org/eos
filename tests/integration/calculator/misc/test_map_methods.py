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


from eos import *
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestMapMethods(CalculatorTestCase):
    """Test map methods not covered by other test cases"""

    def setUp(self):
        super().setUp()
        self.attr1 = self.ch.attribute()
        self.attr2 = self.ch.attribute()
        self.attr3 = self.ch.attribute(default_value=11)
        self.attr4 = self.ch.attribute()
        self.attr5 = self.ch.attribute()
        modifier1 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr1.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.attr5.id
        )
        modifier2 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr2.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.attr5.id
        )
        modifier3 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr3.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.attr5.id
        )
        modifier4 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr4.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.attr5.id
        )
        effect = self.ch.effect(
            category=EffectCategory.passive, modifiers=(modifier1, modifier2, modifier3, modifier4)
        )
        self.item = Implant(self.ch.type(
            effects=[effect], attributes={self.attr1.id: 5, self.attr2.id: 10, self.attr5.id: 4}
        ).id)
        self.fit.implants.add(self.item)

    def calculate_attrs(self, special=()):
        for attr in (self.attr1.id, self.attr2.id, self.attr3.id, self.attr4.id, self.attr5.id, *special):
            self.item.attributes.get(attr)

    def test_getattr(self):
        self.assertAlmostEqual(self.item.attributes[self.attr1.id], 20)
        self.assertAlmostEqual(self.item.attributes[self.attr2.id], 40)
        self.assertAlmostEqual(self.item.attributes[self.attr3.id], 44)
        with self.assertRaises(KeyError):
            self.item.attributes[self.attr4.id]
        self.assertAlmostEqual(self.item.attributes[self.attr5.id], 4)
        with self.assertRaises(KeyError):
            self.item.attributes[1008]
        # Attempts to fetch non-existent attribute and attribute without base value
        # generate errors, which is not related to this test
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(self.fit)

    def test_getattr_no_source(self):
        self.fit.source = None
        with self.assertRaises(KeyError):
            self.item.attributes[self.attr1.id]
        with self.assertRaises(KeyError):
            self.item.attributes[self.attr2.id]
        with self.assertRaises(KeyError):
            self.item.attributes[self.attr3.id]
        with self.assertRaises(KeyError):
            self.item.attributes[self.attr4.id]
        with self.assertRaises(KeyError):
            self.item.attributes[self.attr5.id]
        with self.assertRaises(KeyError):
            self.item.attributes[1008]
        # Attempts to fetch non-existent attribute and attribute without base value
        # generate errors, which is not related to this test
        self.assertEqual(len(self.log), 6)
        self.assert_fit_buffers_empty(self.fit)

    def test_get(self):
        # Make sure map's get method replicates functionality
        # of dictionary get method
        self.assertAlmostEqual(self.item.attributes.get(self.attr1.id), 20)
        self.assertAlmostEqual(self.item.attributes.get(self.attr2.id), 40)
        self.assertAlmostEqual(self.item.attributes.get(self.attr3.id), 44)
        self.assertIsNone(self.item.attributes.get(self.attr4.id))
        self.assertAlmostEqual(self.item.attributes.get(self.attr5.id), 4)
        self.assertIsNone(self.item.attributes.get(1008))
        self.assertEqual(self.item.attributes.get(1008, 60), 60)
        # Attempts to fetch non-existent attribute and attribute without base value
        # generate errors, which is not related to this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(self.fit)

    def test_get_no_source(self):
        self.fit.source = None
        self.assertIsNone(self.item.attributes.get(self.attr1.id))
        self.assertIsNone(self.item.attributes.get(self.attr2.id))
        self.assertIsNone(self.item.attributes.get(self.attr3.id))
        self.assertIsNone(self.item.attributes.get(self.attr4.id))
        self.assertIsNone(self.item.attributes.get(self.attr5.id))
        self.assertIsNone(self.item.attributes.get(1008))
        self.assertEqual(self.item.attributes.get(1008, 60), 60)
        self.assertEqual(len(self.log), 7)
        self.assert_fit_buffers_empty(self.fit)

    def test_len(self):
        # Length should return length, counting unique IDs from
        # both attribute containers. First, values are not calculated
        self.assertEqual(len(self.item.attributes), 3)
        # Force calculation
        self.calculate_attrs(special=[1008])
        # Length should change, as it now includes attr which had no
        # value on item but has default value
        self.assertEqual(len(self.item.attributes), 4)
        # Cleanup
        # Log entries are unrelated to this test
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(self.fit)

    def test_len_no_source(self):
        self.fit.source = None
        self.assertEqual(len(self.item.attributes), 0)
        self.calculate_attrs(special=[1008])
        self.assertEqual(len(self.item.attributes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 6)
        self.assert_fit_buffers_empty(self.fit)

    def test_contains(self):
        # Make sure map reacts positively to items contained
        # in any attribute container, and negatively for attributes
        # which were not found
        self.assertTrue(self.attr1.id in self.item.attributes)
        self.assertTrue(self.attr2.id in self.item.attributes)
        self.assertFalse(self.attr3.id in self.item.attributes)
        self.assertFalse(self.attr4.id in self.item.attributes)
        self.assertTrue(self.attr5.id in self.item.attributes)
        self.assertFalse(1008 in self.item.attributes)
        self.calculate_attrs(special=[1008])
        self.assertTrue(self.attr1.id in self.item.attributes)
        self.assertTrue(self.attr2.id in self.item.attributes)
        self.assertTrue(self.attr3.id in self.item.attributes)
        self.assertFalse(self.attr4.id in self.item.attributes)
        self.assertTrue(self.attr5.id in self.item.attributes)
        self.assertFalse(1008 in self.item.attributes)
        # Cleanup
        # Log entries are unrelated to this test
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(self.fit)

    def test_contains_no_source(self):
        self.fit.source = None
        self.assertFalse(self.attr1.id in self.item.attributes)
        self.assertFalse(self.attr2.id in self.item.attributes)
        self.assertFalse(self.attr3.id in self.item.attributes)
        self.assertFalse(self.attr4.id in self.item.attributes)
        self.assertFalse(self.attr5.id in self.item.attributes)
        self.assertFalse(1008 in self.item.attributes)
        self.calculate_attrs(special=[1008])
        self.assertFalse(self.attr1.id in self.item.attributes)
        self.assertFalse(self.attr2.id in self.item.attributes)
        self.assertFalse(self.attr3.id in self.item.attributes)
        self.assertFalse(self.attr4.id in self.item.attributes)
        self.assertFalse(self.attr5.id in self.item.attributes)
        self.assertFalse(1008 in self.item.attributes)
        # Cleanup
        self.assertEqual(len(self.log), 6)
        self.assert_fit_buffers_empty(self.fit)

    def test_keys(self):
        # When we request map keys, they should include all unique
        # attribute IDs w/o duplication
        self.assertCountEqual(self.item.attributes.keys(), (self.attr1.id, self.attr2.id, self.attr5.id))
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(
            self.item.attributes.keys(),
            (self.attr1.id, self.attr2.id, self.attr3.id, self.attr5.id)
        )
        # Cleanup
        # Log entries are unrelated to this test
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(self.fit)

    def test_keys_no_source(self):
        self.fit.source = None
        self.assertCountEqual(self.item.attributes.keys(), ())
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(self.item.attributes.keys(), ())
        # Cleanup
        self.assertEqual(len(self.log), 6)
        self.assert_fit_buffers_empty(self.fit)

    def test_iter(self):
        # Iter should return the same keys as keys(). CountEqual
        # takes any iterable - we just check its contents here,
        # w/o checking format of returned data
        self.assertCountEqual(self.item.attributes, (self.attr1.id, self.attr2.id, self.attr5.id))
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(self.item.attributes, (self.attr1.id, self.attr2.id, self.attr3.id, self.attr5.id))
        # Cleanup
        # Log entries are unrelated to this test
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(self.fit)

    def test_iter_no_source(self):
        self.fit.source = None
        self.assertCountEqual(self.item.attributes, ())
        self.calculate_attrs(special=[1008])
        self.assertCountEqual(self.item.attributes, ())
        # Cleanup
        self.assertEqual(len(self.log), 6)
        self.assert_fit_buffers_empty(self.fit)
