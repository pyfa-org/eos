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


from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import AttributeId, EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestRounding(CalculatorTestCase):

    def test_cpu_down(self):
        attr = self.ch.attribute(attribute_id=AttributeId.cpu)
        item = Implant(self.ch.type(attributes={attr.id: 2.3333}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[attr.id], 2.33)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_cpu_up(self):
        attr = self.ch.attribute(attribute_id=AttributeId.cpu)
        item = Implant(self.ch.type(attributes={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[attr.id], 2.67)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_cpu_modified(self):
        src_attr = self.ch.attribute()
        tgt_attr = self.ch.attribute(attribute_id=AttributeId.cpu)
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategoryId.passive, modifiers=[modifier])
        item = Implant(self.ch.type(attributes={src_attr.id: 20, tgt_attr.id: 1.9444}, effects=[effect]).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[tgt_attr.id], 2.33)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_cpu_output(self):
        attr = self.ch.attribute(attribute_id=AttributeId.cpu_output)
        item = Implant(self.ch.type(attributes={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[attr.id], 2.67)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_power(self):
        attr = self.ch.attribute(attribute_id=AttributeId.power)
        item = Implant(self.ch.type(attributes={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[attr.id], 2.67)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_power_output(self):
        attr = self.ch.attribute(attribute_id=AttributeId.power_output)
        item = Implant(self.ch.type(attributes={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[attr.id], 2.67)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_other(self):
        attr = self.ch.attribute()
        item = Implant(self.ch.type(attributes={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[attr.id], 2.6666)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
