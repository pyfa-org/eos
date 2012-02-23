#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.eve.attribute import Attribute
from eos.eve.const import Attribute as ConstAttribute
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, Skill
from eos.tests.eosTestCase import EosTestCase


class TestSkillLevel(EosTestCase):
    """Test return value when requesting attribute which isn't set"""

    def testSpecialAttrAccess(self):
        attr = Attribute(ConstAttribute.skillLevel)
        fit = Fit({attr.id: attr})
        skill = Skill(Type(None, attributes={attr.id: 3}))
        skill.level = 5
        fit._addHolder(skill)
        # If holder has level attribute, it must be returned despite of holder contents
        self.assertAlmostEqual(skill.attributes[ConstAttribute.skillLevel], 5)

    def testStandardAttrAccess(self):
        attr = Attribute(ConstAttribute.skillLevel)
        fit = Fit({attr.id: attr})
        skill = IndependentItem(Type(None, attributes={attr.id: 3}))
        fit._addHolder(skill)
        # If .skill direct attribute is not available, standard
        # skill level attribute (from item attributes) should
        # be returned
        self.assertAlmostEqual(skill.attributes[ConstAttribute.skillLevel], 3)
