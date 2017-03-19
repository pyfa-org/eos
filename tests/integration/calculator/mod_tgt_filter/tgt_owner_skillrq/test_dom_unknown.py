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
from eos.const.eos import ModifierTargetFilter, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtOwnerSkillrqDomainTarget(CalculatorTestCase):

    def test_no_effect(self):
        tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.owner_skillrq,
            tgt_domain=1972,
            tgt_filter_extra_arg=56,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        influence_source = Implant(self.ch.type(effects=[effect], attributes={src_attr.id: 20}).id)
        influence_target = Rig(self.ch.type(attributes={tgt_attr.id: 100}, required_skills={56: 1}).id)
        self.fit.rigs.add(influence_target)
        # Action
        self.fit.implants.add(influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
