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


from eos import Fit
from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from tests.integration.testcase import IntegrationTestCase


class EffectModeTestCase(IntegrationTestCase):
    """Class which should be used by effect mode tests.

    With these tests we check in which cases which effects are enabled and
    disabled by running attribute calculation, which may be or may be not
    modified by an effect.

    Attributes:
        fit: Pre-created fit.
        src_attr: Attribute which should be used as modification source.
        tgt_attr: Attribute which should be used as modification target.
        modifier: Modifier which modifies target attribute.
    """

    def setUp(self):
        IntegrationTestCase.setUp(self)
        self.fit = Fit()
        self.src_attr = self.mkattr()
        self.tgt_attr = self.mkattr()
        self.modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=self.tgt_attr.id,
            operator=ModOperator.mod_add,
            affector_attr_id=self.src_attr.id)

    def get_log(self, name='eos.effect_status'):
        return IntegrationTestCase.get_log(self, name=name)
