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


import logging

from eos import Character
from eos import Implant
from eos import Rig
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestTgtDomainSkillrqDomainSelf(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain_skillrq,
            tgt_domain=ModDomain.self,
            tgt_filter_extra_arg=56,
            tgt_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.influence_src_type = self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect])

    def test_ship(self):
        influence_src = Ship(self.influence_src_type.id)
        influence_tgt = Rig(self.mktype(attrs={
            self.tgt_attr.id: 100,
            AttrId.required_skill_1: 56,
            AttrId.required_skill_1_level: 1}).id)
        self.fit.rigs.add(influence_tgt)
        # Action
        self.fit.ship = influence_src
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 120)
        # Action
        self.fit.ship = None
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character(self):
        influence_src = Character(self.influence_src_type.id)
        influence_tgt = Implant(self.mktype(attrs={
            self.tgt_attr.id: 100,
            AttrId.required_skill_1: 56,
            AttrId.required_skill_1_level: 1}).id)
        self.fit.implants.add(influence_tgt)
        # Action
        self.fit.character = influence_src
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_unpositioned_error(self):
        influence_src = Rig(self.influence_src_type.id)
        # Action
        # Here we do not position item in fit, this way attribute calculator
        # won't know that source is 'owner' of some domain and will log
        # corresponding error
        self.fit.rigs.add(influence_src)
        # Verification
        log = self.get_log()
        self.assertEqual(len(log), 2)
        for log_record in log:
            self.assertEqual(log_record.name, 'eos.fit.calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on item type {}: unsupported target '
                'domain 1'.format(self.influence_src_type.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
