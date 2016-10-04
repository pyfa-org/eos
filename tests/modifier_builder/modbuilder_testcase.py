# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.data.cache_generator.modifier_builder import ModifierBuilder
from tests.eos_testcase import EosTestCase
from .environment import ExpressionFactory


class ModBuilderTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.ef -- factory to generate and store expressions
    self.run_builder -- run builder using data from
    expression factory
    """

    def setUp(self):
        super().setUp()
        self.ef = ExpressionFactory()

    def run_builder(self, effect_row):
        effect_row.setdefault('effect_id', 1)
        effect_row.setdefault('pre_expression', None)
        effect_row.setdefault('post_expression', None)
        effect_row.setdefault('modifier_info', None)
        builder = ModifierBuilder(self.ef.data)
        return builder.build(effect_row)
