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

from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtDomainGroupDomainSelf(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attr()
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain_group,
            tgt_domain=ModifierDomain.self,
            tgt_filter_extra_arg=35,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id)
        effect = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier])
        self.src_eve_type = self.ch.type(
            attributes={src_attr.id: 20}, effects=[effect])

    def test_ship(self):
        influence_src = Ship(self.src_eve_type.id)
        influence_tgt = Rig(self.ch.type(
            group=35, attributes={self.tgt_attr.id: 100}).id)
        self.fit.rigs.add(influence_tgt)
        # Action
        self.fit.ship = influence_src
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.ship = None
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character(self):
        influence_src = Character(self.src_eve_type.id)
        influence_tgt = Implant(self.ch.type(
            group=35, attributes={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(influence_tgt)
        # Action
        self.fit.character = influence_src
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.character = None
        # Verification
        self.assertAlmostEqual(influence_tgt.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_unpositioned_error(self):
        influence_src = Implant(self.src_eve_type.id)
        # Action
        # Here we do not position item in fit, this way attribute calculator
        # won't know that source is 'owner' of some domainand will log
        # corresponding error
        self.fit.implants.add(influence_src)
        # Verification
        log = self.get_log()
        self.assertEqual(len(log), 2)
        for log_record in log:
            self.assertEqual(log_record.name, 'eos.fit.calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on eve type {}: unsupported target '
                'domain 1'.format(self.src_eve_type.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
