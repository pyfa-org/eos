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
from eos.const.eos import ModDomain, ModOperator, ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestSrcAttr(CalculatorTestCase):

    def test_absent_attr_combination(self):
        # Check how calculator reacts to source attribute which is absent
        tgt_attr = self.ch.attr()
        abs_attr = self.ch.attr()
        src_attr = self.ch.attr()
        invalid_modifier = self.mod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=abs_attr.id)
        valid_modifier = self.mod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=(invalid_modifier, valid_modifier))
        item_type = self.ch.type(
            attrs={src_attr.id: 1.5, tgt_attr.id: 100}, effects=[effect])
        item = Rig(item_type.id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        # Invalid source value shouldn't screw whole calculation process
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 150)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.INFO)
        self.assertEqual(
            log_record.msg,
            'unable to find base value for attribute {} '
            'on item type {}'.format(abs_attr.id, item_type.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
