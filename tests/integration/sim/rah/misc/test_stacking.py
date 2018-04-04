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


from eos import ModuleLow
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.sim.rah.testcase import RahSimTestCase


class TestRahStacking(RahSimTestCase):

    def test_stacking(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        resmod_src_attr = self.mkattr()
        resmod_mod_em = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_em.id,
            operator=ModOperator.pre_mul,
            src_attr_id=resmod_src_attr.id)
        resmod_mod_therm = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_therm.id,
            operator=ModOperator.pre_mul,
            src_attr_id=resmod_src_attr.id)
        resmod_mod_kin = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_kin.id,
            operator=ModOperator.pre_mul,
            src_attr_id=resmod_src_attr.id)
        resmod_mod_expl = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_expl.id,
            operator=ModOperator.pre_mul,
            src_attr_id=resmod_src_attr.id)
        resmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[
                resmod_mod_em,
                resmod_mod_therm,
                resmod_mod_kin,
                resmod_mod_expl])
        resmod = ModuleLow(self.mktype(
            attrs={resmod_src_attr.id: 0.85},
            effects=[resmod_effect]).id)
        self.fit.modules.low.append(resmod)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.655)
        # These values should be set to ship armor if RAH uses premul operator,
        # otherwise resistances will be better as there will be no stacking
        # penalty
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.425, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.516, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.535, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.513, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
