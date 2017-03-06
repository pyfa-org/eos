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
from tests.calculator.environment import IndependentItem, OwnerModifiableItem


class TestTgtOwnerSkillrqDomainChar(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.owner_skillrq,
            tgt_domain=ModifierDomain.character,
            tgt_filter_extra_arg=56,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier,))
        self.influence_source = IndependentItem(self.ch.type(
            effects=(effect,),
            attributes={src_attr.id: 20}
        ))

    def test_owner_modifiable(self):
        eve_type = self.ch.type(attributes={self.tgt_attr.id: 100})
        eve_type.required_skills = {56: 1}
        influence_target = OwnerModifiableItem(eve_type)
        self.fit.items.add(influence_target)
        # Action
        self.fit.items.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.items.remove(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_not_owner_modifiable(self):
        eve_type = self.ch.type(attributes={self.tgt_attr.id: 100})
        eve_type.required_skills = {56: 1}
        influence_target = IndependentItem(eve_type)
        self.fit.items.add(influence_target)
        # Action
        self.fit.items.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(self.influence_source)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_other_skill(self):
        eve_type = self.ch.type(attributes={self.tgt_attr.id: 100})
        eve_type.required_skills = {87: 1}
        influence_target = OwnerModifiableItem(eve_type)
        self.fit.items.add(influence_target)
        # Action
        self.fit.items.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(self.influence_source)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
