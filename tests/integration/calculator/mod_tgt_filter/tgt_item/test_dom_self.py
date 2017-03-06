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


class TestTgtItemDomainSelf(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        self.src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.src_attr.id
        )
        self.effect = self.ch.effect(category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_independent(self):
        item_type_id = 1
        self.ch.type(
            type_id=item_type_id, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        )
        item = Ship(item_type_id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_parent_domain_character(self):
        item_type_id = 1
        self.ch.type(
            type_id=item_type_id, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        )
        item = Implant(item_type_id)
        # Action
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.implants.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_parent_domain_ship(self):
        item_type_id = 1
        self.ch.type(
            type_id=item_type_id, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        )
        item = Rig(item_type_id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.rigs.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_other(self):
        # Here we check that self-reference modifies only carrier of effect,
        # and nothing else is affected. We position item as character and
        # check another item which has character modifier domain to ensure
        # that items 'belonging' to self are not affected too
        source_type_id = 1
        self.ch.type(
            type_id=source_type_id, effects=(self.effect,),
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}
        )
        influence_source = Character(source_type_id)
        item_type_id = 2
        self.ch.type(type_id=item_type_id, attributes={self.tgt_attr.id: 100})
        item = Implant(item_type_id)
        self.fit.implants.add(item)
        # Action
        self.fit.character = influence_source
        # Verification
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.character = None
        self.fit.implants.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
