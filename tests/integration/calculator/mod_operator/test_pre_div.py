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


class TestOperatorPreDiv(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_div,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        self.influence_source1 = Implant(self.ch.type(effects=[effect], attributes={src_attr.id: 1.2}).id)
        self.influence_source2 = Implant(self.ch.type(effects=[effect], attributes={src_attr.id: 1.5}).id)
        self.influence_source3 = Implant(self.ch.type(effects=[effect], attributes={src_attr.id: 0.1}).id)
        self.influence_source4 = Implant(self.ch.type(effects=[effect], attributes={src_attr.id: 0.75}).id)
        self.influence_source5 = Implant(self.ch.type(effects=[effect], attributes={src_attr.id: 5}).id)
        self.influence_target = Rig(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(self.influence_source1)
        self.fit.implants.add(self.influence_source2)
        self.fit.implants.add(self.influence_source3)
        self.fit.implants.add(self.influence_source4)
        self.fit.implants.add(self.influence_source5)
        self.fit.rigs.add(self.influence_target)

    def test_unpenalized(self):
        self.tgt_attr.stackable = True
        # Verification
        self.assertAlmostEqual(self.influence_target.attributes[self.tgt_attr.id], 148.148, places=3)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_penalized(self):
        self.tgt_attr.stackable = False
        # Verification
        self.assertAlmostEqual(self.influence_target.attributes[self.tgt_attr.id], 165.791, places=3)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
