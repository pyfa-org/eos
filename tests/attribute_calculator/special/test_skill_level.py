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


from eos.const.eve import Attribute
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem, Skill


class TestSkillLevel(AttrCalcTestCase):
    """Test access to skill level via various means"""

    def test_special_attr_access(self):
        attr = self.ch.attribute(attribute_id=Attribute.skill_level)
        skill = Skill(self.ch.type_(type_id=1, attributes={attr.id: 3}))
        skill.level = 5
        self.fit.items.add(skill)
        # If holder has level attribute, it must be returned despite of holder contents
        self.assertEqual(skill.attributes[Attribute.skill_level], 5)
        self.fit.items.remove(skill)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_standard_attr_access(self):
        attr = self.ch.attribute(attribute_id=Attribute.skill_level)
        holder = IndependentItem(self.ch.type_(type_id=1, attributes={attr.id: 3}))
        self.fit.items.add(holder)
        # If .skill direct attribute is not available, standard
        # skill level attribute (from item attributes) should
        # be returned
        self.assertEqual(holder.attributes[Attribute.skill_level], 3)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
