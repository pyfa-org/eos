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
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestOperatorPreMul(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attr()
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.pre_mul,
            src_attr=src_attr.id)
        effect = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier])
        self.influence_src1 = Implant(self.ch.type(
            attributes={src_attr.id: 1.2}, effects=[effect]).id)
        self.influence_src2 = Implant(self.ch.type(
            attributes={src_attr.id: 1.5}, effects=[effect]).id)
        self.influence_src3 = Implant(self.ch.type(
            attributes={src_attr.id: 0.1}, effects=[effect]).id)
        self.influence_src4 = Implant(self.ch.type(
            attributes={src_attr.id: 0.75}, effects=[effect]).id)
        self.influence_src5 = Implant(self.ch.type(
            attributes={src_attr.id: 5}, effects=[effect]).id)
        self.influence_tgt = Rig(self.ch.type(
            attributes={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(self.influence_src1)
        self.fit.implants.add(self.influence_src2)
        self.fit.implants.add(self.influence_src3)
        self.fit.implants.add(self.influence_src4)
        self.fit.implants.add(self.influence_src5)
        self.fit.rigs.add(self.influence_tgt)

    def test_unpenalized(self):
        self.tgt_attr.stackable = True
        # Verification
        self.assertAlmostEqual(
            self.influence_tgt.attributes[self.tgt_attr.id], 67.5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_penalized(self):
        self.tgt_attr.stackable = False
        # Verification
        self.assertAlmostEqual(
            self.influence_tgt.attributes[self.tgt_attr.id], 62.55, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
