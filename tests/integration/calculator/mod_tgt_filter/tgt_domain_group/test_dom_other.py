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
from eos.const.eve import EffectCategory
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtDomainGroupDomainOther(CalculatorTestCase):

    def test_error(self):
        tgt_attr = self.ch.attr()
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain_group,
            tgt_domain=ModifierDomain.other,
            tgt_filter_extra_arg=35,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id)
        effect = self.ch.effect(
            category=EffectCategory.passive, modifiers=[modifier])
        src_eve_type = self.ch.type(
            attributes={src_attr.id: 20}, effects=[effect])
        influence_src = Rig(src_eve_type.id)
        # Action
        # Charge's container or module's charge can't be 'owner'of other items,
        # thus such modification type is unsupported
        self.fit.rigs.add(influence_src)
        # Verification
        log = self.get_log()
        self.assertEqual(len(log), 2)
        for log_record in log:
            self.assertEqual(log_record.name, 'eos.fit.calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on eve type {}: unsupported target '
                'domain {}'.format(src_eve_type.id, ModifierDomain.other))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
