#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.const.eve import Attribute
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import IndependentItem, Skill


class TestSkillLevel(AttrCalcTestCase):
    """Test return value when requesting attribute which isn't set"""

    def testSpecialAttrAccess(self):
        attr = self.ch.attribute(attributeId=Attribute.skillLevel)
        skill = Skill(self.ch.type_(typeId=1, attributes={attr.id: 3}))
        skill.level = 5
        self.fit.items.add(skill)
        # If holder has level attribute, it must be returned despite of holder contents
        self.assertAlmostEqual(skill.attributes[Attribute.skillLevel], 5)
        self.fit.items.remove(skill)
        self.assertEqual(len(self.log), 0)
        self.assertLinkBuffersEmpty(self.fit)

    def testStandardAttrAccess(self):
        attr = self.ch.attribute(attributeId=Attribute.skillLevel)
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={attr.id: 3}))
        self.fit.items.add(holder)
        # If .skill direct attribute is not available, standard
        # skill level attribute (from item attributes) should
        # be returned
        self.assertAlmostEqual(holder.attributes[Attribute.skillLevel], 3)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertLinkBuffersEmpty(self.fit)
