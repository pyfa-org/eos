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


from eos.const.eos import Restriction, Slot
from eos.const.eve import Attribute, Group, Category
from eos.fit.holder.item import *
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestHolderClass(RestrictionTestCase):
    """Check functionality of holder class verification"""

    def testBoosterPass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.implant, attributes={Attribute.boosterness: 3})
        holder = Booster(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testBoosterFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008, attributes={Attribute.boosterness: 3})
        holder = Booster(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Booster)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testBoosterFailAttr(self):
        item = self.ch.type_(typeId=1, categoryId=Category.implant)
        holder = Booster(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Booster)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testCharacterPass(self):
        item = self.ch.type_(typeId=1, groupId=Group.character)
        holder = Character(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testCharacterFailGroup(self):
        item = self.ch.type_(typeId=1, groupId=1008)
        holder = Character(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Character)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testChargePass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.charge)
        holder = Charge(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testChargeFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        holder = Charge(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Charge)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testDronePass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.drone)
        holder = Drone(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testDroneFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        holder = Drone(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Drone)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testEffectBeaconPass(self):
        item = self.ch.type_(typeId=1, groupId=Group.effectBeacon)
        holder = EffectBeacon(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testEffectBeaconFailGroup(self):
        item = self.ch.type_(typeId=1, groupId=1008)
        holder = EffectBeacon(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, EffectBeacon)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testImplantPass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.implant, attributes={Attribute.implantness: 3})
        holder = Implant(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testImplantFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008, attributes={Attribute.implantness: 3})
        holder = Implant(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Implant)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testImplantFailAttr(self):
        item = self.ch.type_(typeId=1, categoryId=Category.implant)
        holder = Implant(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Implant)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testModulePassHigh(self):
        item = self.ch.type_(typeId=1, categoryId=Category.module)
        item.slots = {Slot.moduleHigh}
        holder = Module(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testModulePassMedium(self):
        item = self.ch.type_(typeId=1, categoryId=Category.module)
        item.slots = {Slot.moduleMed}
        holder = Module(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testModulePassLow(self):
        item = self.ch.type_(typeId=1, categoryId=Category.module)
        item.slots = {Slot.moduleLow}
        holder = Module(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testModuleFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        item.slots = {Slot.moduleHigh}
        holder = Module(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Module)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)

    def testModuleFailSlot(self):
        item = self.ch.type_(typeId=1, categoryId=Category.module)
        item.slots = {1008}
        holder = Module(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Module)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testRigPass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.module)
        item.slots = {Slot.rig}
        holder = Rig(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testRigFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        item.slots = {Slot.rig}
        holder = Rig(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Rig)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)

    def testRigFailSlot(self):
        item = self.ch.type_(typeId=1, categoryId=Category.module)
        item.slots = {1008}
        holder = Rig(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Rig)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testShipPass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.ship)
        holder = Ship(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testShipFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        holder = Ship(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Ship)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testSkillPass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.skill)
        holder = Skill(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testSkillFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        holder = Skill(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Skill)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testSubsystemPass(self):
        item = self.ch.type_(typeId=1, categoryId=Category.subsystem)
        item.slots = {Slot.subsystem}
        holder = Subsystem(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testSubsystemFailCategory(self):
        item = self.ch.type_(typeId=1, categoryId=1008)
        holder = Subsystem(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Subsystem)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testSubsystemFailSlot(self):
        item = self.ch.type_(typeId=1, categoryId=Category.subsystem)
        item.slots = {1008}
        holder = Subsystem(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Subsystem)
        self.assertEqual(len(restrictionError.expectedClasses), 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testSingleReplacement(self):
        item = self.ch.type_(typeId=1, categoryId=Category.implant, attributes={Attribute.boosterness: 3})
        holder = Implant(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Implant)
        self.assertEqual(len(restrictionError.expectedClasses), 1)
        self.assertIn(Booster, restrictionError.expectedClasses)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMultipleReplacements(self):
        item = self.ch.type_(typeId=1, categoryId=Category.implant,
                             attributes={Attribute.boosterness: 3, Attribute.implantness: 1})
        holder = Drone(1)
        holder._Holder__type = item
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.holderClass)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.holderClass, Drone)
        self.assertEqual(len(restrictionError.expectedClasses), 2)
        self.assertIn(Booster, restrictionError.expectedClasses)
        self.assertIn(Implant, restrictionError.expectedClasses)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
