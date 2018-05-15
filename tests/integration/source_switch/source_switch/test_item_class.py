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


from eos import Booster
from eos import Character
from eos import Charge
from eos import Drone
from eos import EffectBeacon
from eos import FighterSquad
from eos import Implant
from eos import ModuleHigh
from eos import ModuleLow
from eos import ModuleMid
from eos import Rig
from eos import Ship
from eos import Skill
from eos import Stance
from eos import Subsystem
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModAffecteeFilter
from eos.const.eve import EffectCategoryId
from tests.integration.source_switch.testcase import SourceSwitchTestCase


class TestSourceSwitchItemClass(SourceSwitchTestCase):
    """Check that all item classes switch source properly."""

    def setUp(self):
        SourceSwitchTestCase.setUp(self)
        self.affector_attr_id = self.allocate_attr_id('src1', 'src2')
        self.affectee_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=self.affector_attr_id)
        self.mkattr(src='src2', attr_id=self.affector_attr_id)
        self.mkattr(src='src1', attr_id=self.affectee_attr_id)
        self.mkattr(src='src2', attr_id=self.affectee_attr_id)

    def make_item_types(self):
        """Create item types for source switch test.

        Create item type in both sources. Both items modify target attribute on
        itself: item in source1 will have its value at 18, item in source2 - 14,
        if everything is processed correctly.

        Returns:
            Item type ID.
        """
        modifier_src1 = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_filter_extra_arg=None,
            affectee_attr_id=self.affectee_attr_id,
            operator=ModOperator.mod_add,
            affector_attr_id=self.affector_attr_id)
        modifier_src2 = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_filter_extra_arg=None,
            affectee_attr_id=self.affectee_attr_id,
            operator=ModOperator.post_mul,
            affector_attr_id=self.affector_attr_id)
        effect_src1 = self.mkeffect(
            src='src1',
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_src1])
        effect_src2 = self.mkeffect(
            src='src2',
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_src2])
        item_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=item_type_id,
            attrs={self.affector_attr_id: 5, self.affectee_attr_id: 13},
            effects=[effect_src1])
        self.mktype(
            src='src2',
            type_id=item_type_id,
            attrs={self.affector_attr_id: 2, self.affectee_attr_id: 7},
            effects=[effect_src2])
        return item_type_id

    # Autocharges are tested in separate module

    def test_booster(self):
        booster = Booster(self.make_item_types())
        self.fit.boosters.add(booster)
        self.assertAlmostEqual(booster.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(booster.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_character(self):
        character = Character(self.make_item_types())
        self.fit.character = character
        self.assertAlmostEqual(character.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(character.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_charge(self):
        module = ModuleHigh(self.make_item_types())
        charge = Charge(self.make_item_types())
        module.charge = charge
        self.fit.modules.high.append(module)
        self.assertAlmostEqual(charge.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(charge.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_drone(self):
        drone = Drone(self.make_item_types())
        self.fit.drones.add(drone)
        self.assertAlmostEqual(drone.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(drone.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_effect_beacon(self):
        effect_beacon = EffectBeacon(self.make_item_types())
        self.fit.effect_beacon = effect_beacon
        self.assertAlmostEqual(effect_beacon.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(effect_beacon.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_fighter_squad(self):
        fighter_squad = FighterSquad(self.make_item_types())
        self.fit.fighters.add(fighter_squad)
        self.assertAlmostEqual(fighter_squad.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(fighter_squad.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_implant(self):
        implant = Implant(self.make_item_types())
        self.fit.implants.add(implant)
        self.assertAlmostEqual(implant.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(implant.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_module_high(self):
        module = ModuleHigh(self.make_item_types())
        self.fit.modules.high.append(module)
        self.assertAlmostEqual(module.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(module.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_module_mid(self):
        module = ModuleMid(self.make_item_types())
        self.fit.modules.mid.append(module)
        self.assertAlmostEqual(module.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(module.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_module_low(self):
        module = ModuleLow(self.make_item_types())
        self.fit.modules.low.append(module)
        self.assertAlmostEqual(module.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(module.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_rig(self):
        rig = Rig(self.make_item_types())
        self.fit.rigs.add(rig)
        self.assertAlmostEqual(rig.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(rig.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_ship(self):
        ship = Ship(self.make_item_types())
        self.fit.ship = ship
        self.assertAlmostEqual(ship.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(ship.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_skill(self):
        skill = Skill(self.make_item_types())
        self.fit.skills.add(skill)
        self.assertAlmostEqual(skill.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(skill.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_stance(self):
        stance = Stance(self.make_item_types())
        self.fit.stance = stance
        self.assertAlmostEqual(stance.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(stance.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_subsystem(self):
        subsystem = Subsystem(self.make_item_types())
        self.fit.subsystems.add(subsystem)
        self.assertAlmostEqual(subsystem.attrs[self.affectee_attr_id], 18)
        # Action
        self.fit.solar_system.source = 'src2'
        # Verification
        self.assertAlmostEqual(subsystem.attrs[self.affectee_attr_id], 14)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
