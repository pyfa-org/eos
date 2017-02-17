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
from eos.const.eve import Attribute, Effect, EffectCategory
from tests.integration.integration_testcase import IntegrationTestCase


class TestRahResults(IntegrationTestCase):

    def test_single_run(self):
        # Attribute setup
        max_attr = self.ch.attribute(
            attribute_id=100000, default_value=1.0, high_is_good=False, stackable=False
        )
        cycle_attr = self.ch.attribute(
            attribute_id=100001, high_is_good=False, stackable=True
        )
        shift_attr = self.ch.attribute(
            attribute_id=Attribute.resistance_shift_amount, high_is_good=True, stackable=True
        )
        armor_em, armor_therm, armor_kin, armor_exp = (self.ch.attribute(
            attribute_id=attr, max_attribute=max_attr.id, high_is_good=False, stackable=False
        ) for attr in (
            Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
            Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
        ))
        # Effect setup
        rah_effect = self.ch.effect(
            effect_id=Effect.adaptive_armor_hardener, category=EffectCategory.active,
            duration_attribute=cycle_attr.id
        )
        # Type setup
        ship_type = self.ch.type(type_id=1, attributes={
            armor_em.id: 0.5, armor_therm.id: 0.65, armor_kin.id: 0.75, armor_exp.id: 0.9
        }, effects=())
        rah_type = self.ch.type(type_id=2, attributes={
            armor_em.id: 0.85, armor_therm.id: 0.85, armor_kin.id: 0.85, armor_exp.id: 0.85,
            shift_attr.id: 6, cycle_attr.id: 5.2
        }, effects=(rah_effect,))
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type.id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type.id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # self.assertAlmostEqual(rah_item.attributes[armor_em.id], 0)

