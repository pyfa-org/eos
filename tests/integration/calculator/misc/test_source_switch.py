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


from eos import Fit
from eos import Rig
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestSourceSwitch(CalculatorTestCase):

    def test_switch_item(self):
        # Here we create 2 separate fits with ships affecting it; each ship
        # affects module with different strength. When we pass module from one
        # fit to another, its internal attribute storage should be cleared. If
        # it wasn't cleared, we wouldn't be able to get refreshed value of
        # attribute
        # Setup
        src_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=src_attr_id)
        self.mkattr(src='src2', attr_id=src_attr_id)
        tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=tgt_attr_id)
        self.mkattr(src='src2', attr_id=tgt_attr_id)
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr_id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr_id)
        effect_id = self.allocate_effect_id('src1', 'src2')
        effect_src1 = self.mkeffect(
            src='src1',
            effect_id=effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        effect_src2 = self.mkeffect(
            src='src2',
            effect_id=effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        ship_type_id = self.allocate_type_id('src1', 'src2')
        ship1 = Ship(self.mktype(
            src='src1',
            type_id=ship_type_id,
            attrs={src_attr_id: 10},
            effects=[effect_src1]).id)
        ship2 = Ship(self.mktype(
            src='src2',
            type_id=ship_type_id,
            attrs={src_attr_id: 20},
            effects=[effect_src2]).id)
        item_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(src='src1', type_id=item_type_id, attrs={tgt_attr_id: 50})
        self.mktype(src='src2', type_id=item_type_id, attrs={tgt_attr_id: 50})
        item = Rig(item_type_id)
        fit1 = Fit('src1')
        fit1.ship = ship1
        fit2 = Fit('src2')
        fit2.ship = ship2
        fit1.rigs.add(item)
        self.assertAlmostEqual(item.attrs.get(tgt_attr_id), 55)
        # Action
        fit1.rigs.remove(item)
        fit2.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs.get(tgt_attr_id), 60)
        # Cleanup
        self.assert_fit_buffers_empty(fit1)
        self.assert_fit_buffers_empty(fit2)
        self.assertEqual(len(self.get_log()), 0)

    def test_switch_fit(self):
        # Here we check if attributes are updated if fit gets new source
        # instance
        # Setup
        src_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=src_attr_id)
        self.mkattr(src='src2', attr_id=src_attr_id)
        tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        max_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=tgt_attr_id, max_attr_id=max_attr_id)
        self.mkattr(src='src2', attr_id=tgt_attr_id, max_attr_id=max_attr_id)
        self.mkattr(src='src1', attr_id=max_attr_id, default_value=54.5)
        self.mkattr(src='src2', attr_id=max_attr_id, default_value=88)
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr_id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr_id)
        effect_id = self.allocate_effect_id('src1', 'src2')
        effect_src1 = self.mkeffect(
            src='src1',
            effect_id=effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        effect_src2 = self.mkeffect(
            src='src2',
            effect_id=effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        ship_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=ship_type_id,
            attrs={src_attr_id: 10},
            effects=[effect_src1])
        self.mktype(
            src='src2',
            type_id=ship_type_id,
            attrs={src_attr_id: 20},
            effects=[effect_src2])
        item_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(src='src1', type_id=item_type_id, attrs={tgt_attr_id: 50})
        self.mktype(src='src2', type_id=item_type_id, attrs={tgt_attr_id: 75})
        fit = Fit()
        ship = Ship(ship_type_id)
        item = Rig(item_type_id)
        fit.ship = ship
        fit.rigs.add(item)
        # 50 * 1.1, but capped at 54.5
        self.assertAlmostEqual(item.attrs.get(tgt_attr_id), 54.5)
        # Action
        fit.source = 'src2'
        # Verification
        # 75 * 1.2, but capped at 88
        self.assertAlmostEqual(item.attrs.get(tgt_attr_id), 88)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
