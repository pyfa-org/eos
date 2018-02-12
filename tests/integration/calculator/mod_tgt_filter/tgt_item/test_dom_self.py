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


from eos import Character
from eos import Implant
from eos import Rig
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestTgtItemDomainSelf(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr()
        self.src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=self.src_attr.id)
        self.effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])

    def test_independent(self):
        item = Ship(self.mktype(
            attrs={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_domain_character(self):
        item = Implant(self.mktype(
            attrs={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        # Action
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_domain_ship(self):
        item = Rig(self.mktype(
            attrs={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_other(self):
        # Here we check that self-reference modifies only carrier of effect, and
        # nothing else is affected. We position item as character and check
        # another item which has character modifier domain to ensure that items
        # 'belonging' to self are not affected too
        influence_src = Character(self.mktype(
            attrs={self.tgt_attr.id: 100, self.src_attr.id: 20},
            effects=[self.effect]).id)
        item = Implant(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(item)
        # Action
        self.fit.character = influence_src
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
