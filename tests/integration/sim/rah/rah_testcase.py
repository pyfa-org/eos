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
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.integration_testcase import IntegrationTestCase


class RahSimTestCase(IntegrationTestCase):
    """Class which should be used by RAH simulator tests.

    Attributes:
        fit: Precreated fit, as it's used in almost all tests.
        rah_effect: RAH main effect.
        heat_effect: RAH heat effect.
        max_attr: Attribute which is intended to cap ship resistances.
        cycle_attr: RAH cycle time attribute.
        heat_attr: RAH heat modifier attribute.
        shift_attr: RAH resistance shift amount attribute.
        armor_em: Armor EM resonance attribute.
        armor_therm: Armor thermal resonance attribute.
        armor_kin: Armor kinetic resonance attribute.
        armor_exp: Armor explosive resonance attribute.
    """

    def setUp(self):
        super().setUp()
        # Attribute setup
        self.max_attr = self.ch.attr(
            default_value=1.0, high_is_good=False, stackable=False)
        self.cycle_attr = self.ch.attr(high_is_good=False, stackable=True)
        self.heat_attr = self.ch.attr(high_is_good=False, stackable=True)
        self.shift_attr = self.ch.attr(
            attribute_id=AttributeId.resistance_shift_amount, high_is_good=True,
            stackable=True)
        self.armor_em = self.ch.attr(
            attribute_id=AttributeId.armor_em_damage_resonance,
            max_attribute_id=self.max_attr.id, high_is_good=False,
            stackable=False)
        self.armor_therm = self.ch.attr(
            attribute_id=AttributeId.armor_thermal_damage_resonance,
            max_attribute_id=self.max_attr.id, high_is_good=False,
            stackable=False)
        self.armor_kin = self.ch.attr(
            attribute_id=AttributeId.armor_kinetic_damage_resonance,
            max_attribute_id=self.max_attr.id, high_is_good=False,
            stackable=False)
        self.armor_exp = self.ch.attr(
            attribute_id=AttributeId.armor_explosive_damage_resonance,
            max_attribute_id=self.max_attr.id, high_is_good=False,
            stackable=False)
        # Effect setup
        self.rah_effect = self.ch.effect(
            effect_id=EffectId.adaptive_armor_hardener,
            category_id=EffectCategoryId.active,
            duration_attribute_id=self.cycle_attr.id, customize=True)
        heat_modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr_id=self.cycle_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr_id=self.heat_attr.id)
        self.heat_effect = self.ch.effect(
            category_id=EffectCategoryId.overload, modifiers=[heat_modifier])
        # Miscellateous setup
        self.fit = Fit()

    def make_ship_type(self, resonances):
        """Create ship type with specified resonances."""
        attr_order = (
            self.armor_em.id, self.armor_therm.id, self.armor_kin.id,
            self.armor_exp.id)
        return self.ch.type(attributes=dict(zip(attr_order, resonances)))

    def make_rah_type(
            self, resonances, shift_amount, cycle_time, heat_cycle_mod=-15):
        """Create RAH type with specified attributes."""
        attr_order = (
            self.armor_em.id, self.armor_therm.id, self.armor_kin.id,
            self.armor_exp.id, self.shift_attr.id, self.cycle_attr.id,
            self.heat_attr.id)
        return self.ch.type(
            attributes=dict(zip(
                attr_order,
                (*resonances, shift_amount, cycle_time, heat_cycle_mod))),
            effects=(self.rah_effect, self.heat_effect),
            default_effect=self.rah_effect)

    def get_log(self, name='eos.fit.sim.reactive_armor_hardener*'):
        return super().get_log(name=name)
