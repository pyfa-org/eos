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


from eve2sql.const import Effect


class EosChecker(object):
    """
    Perform series of checks on data, and report any discrepancies
    which break Eos' assumptions.
    """

    def __init__(self, evedb):
        self.evedb = evedb

    def run(self):
        """Control check workflow"""
        # Check if item self-reference doesn't collide with real typeID
        self.__typeSelfReference()
        # Check if items have multiple default effects
        self.__multipleDefaultEffects()
        # Check if module has multiple effects which assign it to
        # high/med/low slot
        self.__collidingModuleRacks()
        # Check that all attributes have sensible values
        self.__attributeValueType()

    def __typeSelfReference(self):
        """Type ID of -1 is reserved to reference carrier of entity in Eos"""
        reserved_type = -1
        types_table = self.evedb["invtypes"]
        typeIDs = types_table.get_columndataset("typeID")
        if reserved_type in typeIDs:
            print("  Check failed: type with ID {0} exists".format(reserved_type))

    def __multipleDefaultEffects(self):
        """Any item must have 1 default effect at max"""
        # Format: {type ID: default effects count}
        defeffects_count = {}
        typeeffects_table = self.evedb["dgmtypeeffects"]
        typeid_idx = typeeffects_table.index_by_name("typeID")
        isdefault_idx = typeeffects_table.index_by_name("isDefault")
        for datarow in typeeffects_table.datarows:
            isdefault = datarow[isdefault_idx]
            # Ignore entries which don't have isDefault flag set
            if bool(isdefault) is not True:
                continue
            # Fill dictionary
            typeid = datarow[typeid_idx]
            if not typeid in defeffects_count:
                defeffects_count[typeid] = 0
            defeffects_count[typeid] += 1
        # Do actual check according to gathered data
        corrupted_types = set()
        for typeid, defcount in defeffects_count.iteritems():
            if defcount > 1:
                corrupted_types.add(typeid)
        # And print out data
        corrupted_num = len(corrupted_types)
        if corrupted_num > 0:
            plu = "" if corrupted_types == 1 else "s"
            corrupted_list = ", ".join(str(typeid) for typeid in sorted(corrupted_types))
            print("  Check failed: {0} type{1} with multiple default effects detected ({2})".format(corrupted_num, plu, corrupted_list))

    def __collidingModuleRacks(self):
        """
        Eos decides to which rack module will belong based on its effect,
        so there should be no collisions.
        """
        # Format: {type ID: count of 'slot' effects}
        takenslots_count = {}
        typeeffects_table = self.evedb["dgmtypeeffects"]
        typeid_idx = typeeffects_table.index_by_name("typeID")
        effectid_idx = typeeffects_table.index_by_name("effectID")
        slot_effects = {Effect.low_power, Effect.high_power, Effect.medium_power}
        for datarow in typeeffects_table.datarows:
            effect = datarow[effectid_idx]
            # Ignore effect references which do not describe slots
            if not effect in slot_effects:
                continue
            typeid = datarow[typeid_idx]
            if not typeid in takenslots_count:
                takenslots_count[typeid] = 0
            takenslots_count[typeid] += 1
        corrupted_types = set()
        for typeid, slotcount in takenslots_count.iteritems():
            if slotcount > 1:
                corrupted_types.add(typeid)
        corrupted_num = len(corrupted_types)
        if corrupted_num > 0:
            plu = "" if corrupted_types == 1 else "s"
            corrupted_list = ", ".join(str(typeid) for typeid in sorted(corrupted_types))
            print("  Check failed: {0} type{1} with multiple slot effects detected ({2})".format(corrupted_num, plu, corrupted_list))

    def __attributeValueType(self):
        """
        Eos assumes that all attributes on all items contain some numerical
        value.
        """
        corrupted_types = set()
        typeattribs_table = self.evedb["dgmtypeattribs"]
        typeid_idx = typeattribs_table.index_by_name("typeID")
        value_idx = typeattribs_table.index_by_name("value")
        for datarow in typeattribs_table.datarows:
            # All values which cannot be represented by
            # integer or floats are considered as invalid
            if isinstance(datarow[value_idx], (int, float)) is not True:
                corrupted_types.add(datarow[typeid_idx])
        corrupted_num = len(corrupted_types)
        if corrupted_num > 0:
            plu = "" if corrupted_types == 1 else "s"
            corrupted_list = ", ".join(str(typeid) for typeid in sorted(corrupted_types))
            print("  Check failed: {0} type{1} with invalid attribute values detected ({2})".format(corrupted_num, plu, corrupted_list))
