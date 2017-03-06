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


from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtItemAwaitingDomainOther(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        self.src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.other,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.src_attr.id
        )
        self.effect = self.ch.effect(category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_other_container(self):
        influence_source = ContainerItem(self.ch.type(
            effects=(self.effect,),
            attributes={self.src_attr.id: 20}
        ))
        self.fit.items.add(influence_source)
        influence_target = ChargeItem(self.ch.type(
            attributes={self.tgt_attr.id: 100}
        ))
        # Action
        # Here we add influence target after adding source, to make sure
        # modifiers wait for target to appear, and then are applied onto it
        influence_source.charge = influence_target
        influence_target.container = influence_source
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(influence_target)
        influence_target.container = None
        influence_source.charge = None
        self.fit.items.remove(influence_source)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_other_charge(self):
        influence_source = ChargeItem(self.ch.type(
            effects=(self.effect,),
            attributes={self.src_attr.id: 20}
        ))
        self.fit.items.add(influence_source)
        influence_target = ContainerItem(self.ch.type(
            attributes={self.tgt_attr.id: 100}
        ))
        # Action
        # Here we add influence target after adding source, to make sure
        # modifiers wait for target to appear, and then are applied onto it
        influence_source.container = influence_target
        influence_target.charge = influence_source
        self.fit.items.add(influence_target)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.items.remove(influence_target)
        influence_target.charge = None
        influence_source.container = None
        self.fit.items.remove(influence_source)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
