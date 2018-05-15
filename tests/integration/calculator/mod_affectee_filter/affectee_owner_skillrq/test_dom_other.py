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

from eos import Rig
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModAffecteeFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestAffecteeOwnerSkillrqDomainOther(CalculatorTestCase):

    def test_error(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.owner_skillrq,
            affectee_domain=ModDomain.other,
            affectee_filter_extra_arg=56,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        influence_src_type = self.mktype(
            attrs={src_attr.id: 20},
            effects=[effect])
        influence_src = Rig(influence_src_type.id)
        # Action
        # Charge's container or module's charge can't be 'owner' of other items,
        # thus such modification type is unsupported
        self.fit.rigs.add(influence_src)
        # Verification
        self.assert_log_entries(2)
        for log_record in self.log:
            self.assertEqual(log_record.name, 'eos.calculator.affection')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on item type {}: '
                'unsupported affectee domain {}'.format(
                    influence_src_type.id, ModDomain.other))
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
