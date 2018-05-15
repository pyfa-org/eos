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

from eos import Character
from eos import Implant
from eos import Rig
from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModAffecteeFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestTgtDomainDomainSelf(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.self,
            affectee_attr_id=self.tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        self.influence_src_type = self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect])

    def test_ship(self):
        influence_src = Ship(self.influence_src_type.id)
        influence_tgt = Rig(self.mktype(attrs={self.tgt_attr.id: 100}).id)
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
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_character(self):
        influence_src = Character(self.influence_src_type.id)
        influence_tgt = Implant(self.mktype(attrs={self.tgt_attr.id: 100}).id)
        self.fit.implants.add(influence_tgt)
        # Action
        self.fit.character = influence_src
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 120)
        # Action
        self.fit.character = None
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[self.tgt_attr.id], 100)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_unpositioned_error(self):
        influence_src = Implant(self.influence_src_type.id)
        # Action
        # Here we do not position item in fit, this way attribute calculator
        # won't know that source is 'owner' of some domain and will log
        # corresponding error
        self.fit.implants.add(influence_src)
        # Verification
        self.assert_log_entries(2)
        for log_record in self.log:
            self.assertEqual(log_record.name, 'eos.calculator.affection')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on item type {}: '
                'unsupported affectee domain 1'.format(
                    self.influence_src_type.id))
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
