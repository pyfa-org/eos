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
from eos.const.eve import EffectCategory
from tests.integration.sim.rah.rah_testcase import RahSimTestCase


class TestRahSimAttributeOverride(RahSimTestCase):

    def test_rah_modified_resonance_update(self):
        # Setup
        skill_attr = self.ch.attr(high_is_good=False, stackable=False)
        skill_modifiers = tuple(
            self.mod(
                tgt_filter=ModifierTargetFilter.domain,
                tgt_domain=ModifierDomain.ship,
                tgt_attr=attr,
                operator=ModifierOperator.post_mul,
                src_attr=skill_attr.id)
            for attr in (
                self.armor_em.id, self.armor_therm.id, self.armor_kin.id,
                self.armor_exp.id))
        skill_effect = self.ch.effect(
            category=EffectCategory.passive, modifiers=skill_modifiers)
        skill_eve_type = self.ch.type(
            attributes={skill_attr.id: 0.5}, effects=[skill_effect])
        ship_item = Ship(self.make_ship_eve_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship_item
        rah_item = ModuleLow(
            self.make_rah_eve_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.online)
        self.fit.modules.low.equip(rah_item)
        skill_item = Skill(skill_eve_type.id)
        # Force resonance calculation
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Switch state up to enable RAH
        rah_item.state = State.active
        # callbacks are installed, sim is doing its job
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(
            ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Action
        self.fit.skills.add(skill_item)
        rah_item.state = State.online
        # Verification
        # Despite all changes were masked by override, we should have correct
        # values after overrides are removed
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.425)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.425)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.425)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.425)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_override_priority(self):
        # Setup
        ship_item = Ship(self.make_ship_eve_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship_item
        rah_item = ModuleLow(
            self.make_rah_eve_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.online)
        self.fit.modules.low.equip(rah_item)
        # Calculate modified values
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Action
        rah_item.state = State.active
        # Verification
        # Make sure override values are returned, even when modified values were
        # stored
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(
            ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
