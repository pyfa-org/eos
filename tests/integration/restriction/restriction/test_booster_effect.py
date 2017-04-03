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
from eos.const.eve import EffectCategory
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestBoosterEffect(RestrictionTestCase):
    """Check functionality of booster's hidden effects restriction"""

    def setUp(self):
        super().setUp()
        # Create attribs for both handlers
        self.chance_attr1_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=self.chance_attr1_id)
        self.ch2.attribute(attribute_id=self.chance_attr1_id)
        self.chance_attr2_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=self.chance_attr2_id)
        self.ch2.attribute(attribute_id=self.chance_attr2_id)
        # Second handler doesn't have 3rd and 4th attributes
        self.chance_attr3_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=self.chance_attr3_id)
        self.chance_attr4_id = self.allocate_attribute_id(self.ch, self.ch2)
        self.ch.attribute(attribute_id=self.chance_attr4_id)
        # Create effects for both handlers
        self.effect1_id = self.allocate_effect_id(self.ch, self.ch2)
        effect1_src1 = self.ch.effect(
            effect_id=self.effect1_id, category=EffectCategory.passive,
            fitting_usage_chance_attribute=self.chance_attr1_id
        )
        effect1_src2 = self.ch2.effect(
            effect_id=self.effect1_id, category=EffectCategory.passive,
            fitting_usage_chance_attribute=self.chance_attr1_id
        )
        self.effect2_id = self.allocate_effect_id(self.ch, self.ch2)
        effect2_src1 = self.ch.effect(
            effect_id=self.effect2_id, category=EffectCategory.passive,
            fitting_usage_chance_attribute=self.chance_attr2_id
        )
        effect2_src2 = self.ch2.effect(
            effect_id=self.effect2_id, category=EffectCategory.passive,
            fitting_usage_chance_attribute=self.chance_attr2_id
        )
        # Second handler has 3rd effect as normal effect
        self.effect3_id = self.allocate_effect_id(self.ch, self.ch2)
        effect3_src1 = self.ch.effect(
            effect_id=self.effect3_id, category=EffectCategory.passive,
            fitting_usage_chance_attribute=self.chance_attr3_id
        )
        effect3_src2 = self.ch2.effect(effect_id=self.effect3_id, category=EffectCategory.passive)
        # Second handler has no 4th effect at all
        self.effect4_id = self.allocate_effect_id(self.ch, self.ch2)
        effect4_src1 = self.ch.effect(
            effect_id=self.effect4_id, category=EffectCategory.passive,
            fitting_usage_chance_attribute=self.chance_attr4_id
        )
        # Regular effect on both
        self.effect5_id = self.allocate_effect_id(self.ch, self.ch2)
        effect5_src1 = self.ch.effect(effect_id=self.effect5_id, category=EffectCategory.passive)
        effect5_src2 = self.ch2.effect(effect_id=self.effect5_id, category=EffectCategory.passive)
        # Create EVE types
        self.booster_type_id = self.allocate_type_id(self.ch, self.ch2)
        self.ch.type(
            type_id=self.booster_type_id, attributes={
                self.chance_attr1_id: 0.2, self.chance_attr2_id: 0.4,
                self.chance_attr3_id: 0.6, self.chance_attr4_id: 0.8,
            }, effects=(effect1_src1, effect2_src1, effect3_src1, effect4_src1, effect5_src1)
        )
        self.ch2.type(
            type_id=self.booster_type_id, attributes={self.chance_attr1_id: 0.2, self.chance_attr2_id: 0.4},
            effects=(effect1_src2, effect2_src2, effect3_src2, effect5_src2)
        )

    def test_fail(self):
        # Check if error is raised when there's disabled effect
        fit = Fit()
        item = Booster(self.booster_type_id)
        fit.boosters.add(item)
        item.set_side_effect_status(self.effect3_id, False)
        item.set_side_effect_status(self.effect4_id, False)
        fit.source = 'src2'
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.illegally_disabled, {self.effect3_id})
        self.assertEqual(restriction_error.disablable, {self.effect1_id, self.effect2_id})
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_disabled_side_effect(self):
        fit = Fit()
        item = Booster(self.booster_type_id)
        fit.boosters.add(item)
        item.set_side_effect_status(self.effect1_id, False)
        item.set_side_effect_status(self.effect2_id, False)
        fit.source = 'src2'
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_non_booster(self):
        fit = Fit()
        item = Implant(self.booster_type_id)
        fit.implants.add(item)
        item._set_effect_activability(self.effect3_id, True)
        item._set_effect_activability(self.effect4_id, False)
        fit.source = 'src2'
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
