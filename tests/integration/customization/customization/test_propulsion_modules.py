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


import logging

from eos import ModuleLow
from eos import ModuleMid
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.customization.testcase import CustomizationTestCase


class TestPropulsionModules(CustomizationTestCase):

    def setUp(self):
        CustomizationTestCase.setUp(self)
        # Ship attrs
        self.mkattr(attr_id=AttrId.mass)
        self.mkattr(attr_id=AttrId.max_velocity, stackable=False)
        self.mkattr(attr_id=AttrId.signature_radius, stackable=False)
        # Prop mod attrs
        self.mkattr(attr_id=AttrId.mass_addition)
        self.mkattr(attr_id=AttrId.signature_radius_bonus)
        self.mkattr(attr_id=AttrId.speed_factor)
        self.mkattr(attr_id=AttrId.speed_boost_factor)

    def make_ship(self):
        return Ship(self.mktype(attrs={
            AttrId.max_velocity: 455,
            AttrId.signature_radius: 32,
            AttrId.mass: 1050000}).id)

    def make_prop_mod(self, effect_id):
        effect = self.mkeffect(
            effect_id=effect_id,
            category_id=EffectCategoryId.active)
        return ModuleMid(self.mktype(
            attrs={
                AttrId.mass_addition: 500000,
                AttrId.signature_radius_bonus: 410,
                AttrId.speed_factor: 518,
                AttrId.speed_boost_factor: 1500000},
            effects=[effect],
            default_effect=effect).id)

    def test_ab(self):
        ship = self.make_ship()
        ab = self.make_prop_mod(EffectId.module_bonus_afterburner)
        ab.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(ab)
        # Verification
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 2735.871, places=3)
        self.assertAlmostEqual(ship.attrs[AttrId.signature_radius], 32)
        self.assertAlmostEqual(ship.attrs[AttrId.mass], 1550000)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ab_state(self):
        ship = self.make_ship()
        ab = self.make_prop_mod(EffectId.module_bonus_afterburner)
        ab.state = State.online
        self.fit.ship = ship
        self.fit.modules.mid.append(ab)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        self.assertAlmostEqual(ship.attrs[AttrId.signature_radius], 32)
        self.assertAlmostEqual(ship.attrs[AttrId.mass], 1050000)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mwd(self):
        ship = self.make_ship()
        mwd = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        mwd.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(mwd)
        # Verification
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 2735.871, places=3)
        self.assertAlmostEqual(ship.attrs[AttrId.signature_radius], 163.2)
        self.assertAlmostEqual(ship.attrs[AttrId.mass], 1550000)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mwd_state(self):
        ship = self.make_ship()
        mwd = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        mwd.state = State.online
        self.fit.ship = ship
        self.fit.modules.mid.append(mwd)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        self.assertAlmostEqual(ship.attrs[AttrId.signature_radius], 32)
        self.assertAlmostEqual(ship.attrs[AttrId.mass], 1050000)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_ship_not_loaded(self):
        # Here we check that ship which isn't loaded is not causing any severe
        # effects like crashes
        ship = Ship(self.allocate_type_id())
        mwd = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        mwd.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(mwd)
        # Verification
        with self.assertRaises(KeyError):
            ship.attrs[AttrId.max_velocity]
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_isolation(self):
        # When velocity cannot be modified due to errors, sig and mass still
        # should be successfully modified
        ship = self.make_ship()
        propmod_effect = self.mkeffect(
            effect_id=EffectId.module_bonus_microwarpdrive,
            category_id=EffectCategoryId.active)
        propmod = ModuleMid(self.mktype(
            attrs={
                AttrId.mass_addition: 500000,
                AttrId.signature_radius_bonus: 410,
                AttrId.speed_boost_factor: 1500000},
            effects=[propmod_effect],
            default_effect=propmod_effect).id)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        self.assertAlmostEqual(ship.attrs[AttrId.signature_radius], 163.2)
        self.assertAlmostEqual(ship.attrs[AttrId.mass], 1550000)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_ship_attr_mass_absent(self):
        ship = Ship(self.mktype(attrs={
            AttrId.max_velocity: 455,
            AttrId.signature_radius: 32}).id)
        propmod = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_ship_attr_mass_zero(self):
        ship = Ship(self.mktype(attrs={
            AttrId.max_velocity: 455,
            AttrId.signature_radius: 32,
            AttrId.mass: 0}).id)
        propmod_effect = self.mkeffect(
            effect_id=EffectId.module_bonus_microwarpdrive,
            category_id=EffectCategoryId.active)
        propmod = ModuleMid(self.mktype(
            attrs={
                AttrId.mass_addition: 0,
                AttrId.signature_radius_bonus: 410,
                AttrId.speed_factor: 518,
                AttrId.speed_boost_factor: 1500000},
            effects=[propmod_effect],
            default_effect=propmod_effect).id)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.eve_obj.custom.propulsion_modules.modifier.python')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'cannot calculate propulsion speed boost due to zero ship mass')
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)

    def test_velocity_modifier_propmod_attr_speed_boost_absent(self):
        ship = self.make_ship()
        propmod_effect = self.mkeffect(
            effect_id=EffectId.module_bonus_microwarpdrive,
            category_id=EffectCategoryId.active)
        propmod = ModuleMid(self.mktype(
            attrs={
                AttrId.mass_addition: 500000,
                AttrId.signature_radius_bonus: 410,
                AttrId.speed_boost_factor: 1500000},
            effects=[propmod_effect],
            default_effect=propmod_effect).id)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_propmod_attr_thrust_absent(self):
        ship = self.make_ship()
        propmod_effect = self.mkeffect(
            effect_id=EffectId.module_bonus_microwarpdrive,
            category_id=EffectCategoryId.active)
        propmod = ModuleMid(self.mktype(
            attrs={
                AttrId.mass_addition: 500000,
                AttrId.signature_radius_bonus: 410,
                AttrId.speed_factor: 518},
            effects=[propmod_effect],
            default_effect=propmod_effect).id)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 455)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_recalc_ship_attr_mass_changed(self):
        massmod_src_attr = self.mkattr()
        massmod_mod = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.mass,
            operator=ModOperator.mod_add,
            src_attr_id=massmod_src_attr.id)
        massmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[massmod_mod])
        massmod = ModuleLow(self.mktype(
            attrs={massmod_src_attr.id: 400000},
            effects=[massmod_effect]).id)
        ship = self.make_ship()
        propmod = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 2735.871, places=3)
        # Action
        self.fit.modules.low.append(massmod)
        # Verification
        self.assertAlmostEqual(ship.attrs[AttrId.max_velocity], 2268)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_recalc_propmod_attr_speed_boost_changed(self):
        boostmod_src_attr = self.mkattr()
        boostmod_mod = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.speed_factor,
            operator=ModOperator.post_percent,
            src_attr_id=boostmod_src_attr.id)
        boostmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[boostmod_mod])
        boostmod = ModuleLow(self.mktype(
            attrs={boostmod_src_attr.id: 50},
            effects=[boostmod_effect]).id)
        ship = self.make_ship()
        propmod = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 2735.871, places=3)
        # Action
        self.fit.modules.low.append(boostmod)
        # Verification
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 3876.306, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_velocity_modifier_recalc_propmod_attr_thrust_changed(self):
        thrustmod_src_attr = self.mkattr()
        thrustmod_mod = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.speed_boost_factor,
            operator=ModOperator.mod_add,
            src_attr_id=thrustmod_src_attr.id)
        thrustmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[thrustmod_mod])
        thrustmod = ModuleLow(self.mktype(
            attrs={thrustmod_src_attr.id: 500000},
            effects=[thrustmod_effect]).id)
        ship = self.make_ship()
        propmod = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        propmod.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(propmod)
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 2735.871, places=3)
        # Action
        self.fit.modules.low.append(thrustmod)
        # Verification
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 3496.161, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stacking_velocity(self):
        ship = self.make_ship()
        mwd = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        mwd.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(mwd)
        sigmod_src_attr = self.mkattr()
        sigmod_mod = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.max_velocity,
            operator=ModOperator.post_mul,
            src_attr_id=sigmod_src_attr.id)
        sigmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[sigmod_mod])
        sigmod = ModuleLow(self.mktype(
            attrs={sigmod_src_attr.id: 1.1},
            effects=[sigmod_effect]).id)
        self.fit.modules.low.append(sigmod)
        # Verification
        # One of modules are stacking penalized, if they were not, value would
        # be higher
        self.assertAlmostEqual(
            ship.attrs[AttrId.max_velocity], 2973.651, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stacking_signature(self):
        ship = self.make_ship()
        mwd = self.make_prop_mod(EffectId.module_bonus_microwarpdrive)
        mwd.state = State.active
        self.fit.ship = ship
        self.fit.modules.mid.append(mwd)
        sigmod_src_attr = self.mkattr()
        sigmod_mod = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.signature_radius,
            operator=ModOperator.post_percent,
            src_attr_id=sigmod_src_attr.id)
        sigmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[sigmod_mod])
        sigmod = ModuleLow(self.mktype(
            attrs={sigmod_src_attr.id: 10},
            effects=[sigmod_effect]).id)
        self.fit.modules.low.append(sigmod)
        # Verification
        # One of modules are stacking penalized, if they were not, value would
        # be higher
        self.assertAlmostEqual(
            ship.attrs[AttrId.signature_radius], 177.384, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
