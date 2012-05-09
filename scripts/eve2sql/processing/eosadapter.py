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


import collections
import re

from eve2sql.const import DataType, Type, Group, Category, Attribute, AttributeCategory, Operand
from .preprocessor import Preprocessor


class TableType(object):
    """Describes type of table"""
    base = 1  # Defines some entity
    auxiliary = 2  # Auxiliary table, complements some entity with data or serves as link between several other base tables


# Auxiliary named tuples for use with custom database structure specification
TableSpec = collections.namedtuple("TableSpec", ("columns", "strong"))
ColumnSpec = collections.namedtuple("ColumnSpec", ("pk", "fk", "index", "strongvals"))


class EosAdapter(object):
    """
    Adapt data for use in Eos before dumping.
    """
    def __init__(self, evedb):
        self.evedb = evedb

    def run(self):
        """Control database refactoring workflow"""
        # Before cleaning database according to specification, run attribute
        # normalization - it will move all attributes to typeattribs table;
        # if it's done after, we may lack some data required for process
        self.__normalize_attrs()
        # Transform literal references to IDs in expressions table too,
        # before required data is removed
        self.__expression_idzing()
        # Merge multiple language tables into one, we need this to ease
        # of data filtering (more straight-forward FK references)
        self.__combine_translations()
        # Run helper method which will be needed for proper autocleanup
        attrcat_attrid_map = self.__define_attrvalue_relationships_hamster()
        # Assign database format specification to object for ease of use and
        # modification on the fly
        self.dbspec = self.__get_dbspec()
        # Delete malformed entries in both structures; also, fill actual data
        # with additional flags taken from custom data specification
        self.__synch_dbinfo()
        # Container to store signs of so-called strong data, such rows are immune to removal
        # Format: {table name: {column index: {exception values}}
        strong_data = {}
        # Fill it with manually specified data
        self.__process_manual_strongs(strong_data)
        # Mark types we want to keep and metadata as strong
        self.__invtypes_pumping(strong_data)
        self.__metadata_pumping(strong_data)
        # Create data structure for removed data, we need it for proper resulting
        # statistics and in case if we want to put something back
        # Format: {table name: {data rows}}
        trashed_data = {}
        # Automatically clean up data we don't need
        self.__autocleanup(strong_data, trashed_data, attrcat_attrid_map)
        # Print some statistics to know what has been cleaned
        self.__print_stats(trashed_data)
        return

    def __get_dbspec(self):
        """Return specification of data Eos needs"""
        dataspec = {}

        dataspec["dgmattribs"] = TableSpec({}, False)
        dgmattribs = dataspec["dgmattribs"].columns
        dgmattribs["attributeID"] = ColumnSpec(True, None, False, set())
        dgmattribs["attributeName"] = ColumnSpec(False, None, False, set())
        #dgmattribs["attributeCategory"] = ColumnSpec(False, None, False, set())
        dgmattribs["maxAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        #dgmattribs["chargeRechargeTimeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmattribs["defaultValue"] = ColumnSpec(False, None, False, set())
        dgmattribs["published"] = ColumnSpec(False, None, False, set())
        dgmattribs["unitID"] = ColumnSpec(False, "eveunits.unitID", False, set())
        dgmattribs["stackable"] = ColumnSpec(False, None, False, set())
        dgmattribs["highIsGood"] = ColumnSpec(False, None, False, set())
        dgmattribs["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        dgmattribs["displayNameID"] = ColumnSpec(False, "trntexts.textID", False, set())

        dataspec["dgmeffects"] = TableSpec({}, False)
        dgmeffects = dataspec["dgmeffects"].columns
        dgmeffects["effectID"] = ColumnSpec(True, None, False, set())
        dgmeffects["effectName"] = ColumnSpec(False, None, False, set())
        dgmeffects["preExpression"] = ColumnSpec(False, "dgmexpressions.expressionID", False, set())
        dgmeffects["postExpression"] = ColumnSpec(False, "dgmexpressions.expressionID", False, set())
        dgmeffects["effectCategory"] = ColumnSpec(False, None, False, set())
        dgmeffects["isOffensive"] = ColumnSpec(False, None, False, set())
        dgmeffects["isAssistance"] = ColumnSpec(False, None, False, set())
        dgmeffects["durationAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmeffects["trackingSpeedAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmeffects["dischargeAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmeffects["rangeAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmeffects["falloffAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmeffects["fittingUsageChanceAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmeffects["iconID"] = ColumnSpec(False, "icons.iconID", False, set())

        dataspec["dgmexpressions"] = TableSpec({}, False)
        dgmexpressions = dataspec["dgmexpressions"].columns
        dgmexpressions["expressionID"] = ColumnSpec(True, None, False, set())
        dgmexpressions["operandID"] = ColumnSpec(False, None, False, set())
        dgmexpressions["arg1"] = ColumnSpec(False, "dgmexpressions.expressionID", False, set())
        dgmexpressions["arg2"] = ColumnSpec(False, "dgmexpressions.expressionID", False, set())
        dgmexpressions["expressionValue"] = ColumnSpec(False, None, False, set())
        dgmexpressions["expressionTypeID"] = ColumnSpec(False, "invtypes.typeID", False, set())
        dgmexpressions["expressionGroupID"] = ColumnSpec(False, "invgroups.groupID", False, set())
        dgmexpressions["expressionAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())

        dataspec["dgmtypeattribs"] = TableSpec({}, False)
        dgmtypeattribs = dataspec["dgmtypeattribs"].columns
        dgmtypeattribs["typeID"] = ColumnSpec(True, "invtypes.typeID", False, set())
        dgmtypeattribs["attributeID"] = ColumnSpec(True, "dgmattribs.attributeID", False, set())
        dgmtypeattribs["value"] = ColumnSpec(False, None, False, set())

        dataspec["dgmtypeeffects"] = TableSpec({}, False)
        dgmtypeeffects = dataspec["dgmtypeeffects"].columns
        dgmtypeeffects["typeID"] = ColumnSpec(True, "invtypes.typeID", False, set())
        dgmtypeeffects["effectID"] = ColumnSpec(True, "dgmeffects.effectID", False, set())
        dgmtypeeffects["isDefault"] = ColumnSpec(False, None, False, set())

        dataspec["eveunits"] = TableSpec({}, False)
        eveunits = dataspec["eveunits"].columns
        eveunits["unitID"] = ColumnSpec(True, None, False, set())
        eveunits["displayNameID"] = ColumnSpec(False, "trntexts.textID", False, set())
        eveunits["descriptionID"] = ColumnSpec(False, "trntexts.textID", False, set())

        dataspec["icons"] = TableSpec({}, False)
        icons = dataspec["icons"].columns
        icons["iconID"] = ColumnSpec(True, None, False, {0})
        icons["iconFile"] = ColumnSpec(False, None, False, set())

        dataspec["invcategories"] = TableSpec({}, False)
        invcategories = dataspec["invcategories"].columns
        invcategories["categoryID"] = ColumnSpec(True, None, False, set())
        invcategories["categoryNameID"] = ColumnSpec(False, "trntexts.textID", False, set())

        dataspec["invgroups"] = TableSpec({}, False)
        invgroups = dataspec["invgroups"].columns
        invgroups["groupID"] = ColumnSpec(True, None, False, set())
        invgroups["categoryID"] = ColumnSpec(False, "invcategories.categoryID", False, set())
        invgroups["fittableNonSingleton"] = ColumnSpec(False, None, False, set())
        invgroups["published"] = ColumnSpec(False, None, False, set())
        invgroups["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        invgroups["groupNameID"] = ColumnSpec(False, "trntexts.textID", False, set())

        dataspec["invmarketgroups"] = TableSpec({}, False)
        invmarketgroups = dataspec["invmarketgroups"].columns
        invmarketgroups["parentGroupID"] = ColumnSpec(False, "invmarketgroups.marketGroupID", False, set())
        invmarketgroups["marketGroupID"] = ColumnSpec(True, None, False, set())
        invmarketgroups["marketGroupName"] = ColumnSpec(False, None, False, set())
        #invmarketgroups["description"] = ColumnSpec(False, None, False, set())
        invmarketgroups["hasTypes"] = ColumnSpec(False, None, False, set())
        invmarketgroups["iconID"] = ColumnSpec(False, "icons.iconID", False, set())

        dataspec["invmetagroups"] = TableSpec({}, False)
        invmetagroups = dataspec["invmetagroups"].columns
        invmetagroups["metaGroupID"] = ColumnSpec(True, None, False, set())
        invmetagroups["metaGroupNameID"] = ColumnSpec(False, "trntexts.textID", False, set())

        dataspec["invmetatypes"] = TableSpec({}, False)
        invmetatypes = dataspec["invmetatypes"].columns
        invmetatypes["typeID"] = ColumnSpec(True, "invtypes.typeID", False, set())
        invmetatypes["parentTypeID"] = ColumnSpec(False, "invtypes.typeID", False, set())
        invmetatypes["metaGroupID"] = ColumnSpec(False, "invmetagroups.metaGroupID", False, set())

        dataspec["invtypes"] = TableSpec({}, True)
        invtypes = dataspec["invtypes"].columns
        invtypes["typeID"] = ColumnSpec(True, None, False, {Type.character_static})
        invtypes["groupID"] = ColumnSpec(False, "invgroups.groupID", False, set())
        invtypes["raceID"] = ColumnSpec(False, None, False, set())
        invtypes["published"] = ColumnSpec(False, None, False, set())
        invtypes["marketGroupID"] = ColumnSpec(False, "invmarketgroups.marketGroupID", False, set())
        invtypes["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        invtypes["typeNameID"] = ColumnSpec(False, "trntexts.textID", False, set())
        invtypes["descriptionID"] = ColumnSpec(False, "trntexts.textID", False, set())

        dataspec["metadata"] = TableSpec({}, False)
        metadata = dataspec["metadata"].columns
        metadata["fieldName"] = ColumnSpec(True, None, False, set())
        metadata["fieldValue"] = ColumnSpec(False, None, False, set())

        dataspec["trntexts"] = TableSpec({}, False)
        trntexts = dataspec["trntexts"].columns
        trntexts["textID"] = ColumnSpec(True, None, False, set())
        trntexts["de"] = ColumnSpec(False, None, False, set())
        trntexts["en-us"] = ColumnSpec(False, None, False, set())
        trntexts["ja"] = ColumnSpec(False, None, False, set())
        trntexts["ru"] = ColumnSpec(False, None, False, set())

        return dataspec

    def run_old(self):
        """Temporary method to support old database layout"""
        attrcat_attrid_map = self.__define_attrvalue_relationships_hamster()
        dataspec = {}
        dataspec["dgmattribs"] = TableSpec({}, False)
        dgmattribs = dataspec["dgmattribs"].columns
        dgmattribs["attributeID"] = ColumnSpec(True, None, False, set())
        dgmattribs["attributeName"] = ColumnSpec(False, None, False, {"mass", "volume", "capacity", "radius", "neutReflectAmount",
                                                                      "neutReflector", "nosReflectAmount", "nosReflector"})
        dgmattribs["description"] = ColumnSpec(False, None, False, set())
        dgmattribs["defaultValue"] = ColumnSpec(False, None, False, set())
        dgmattribs["published"] = ColumnSpec(False, None, False, set())
        dgmattribs["maxAttributeID"] = ColumnSpec(False, "dgmattribs.attributeID", False, set())
        dgmattribs["displayName"] = ColumnSpec(False, None, False, set())
        dgmattribs["unitID"] = ColumnSpec(False, "eveunits.unitID", False, set())
        dgmattribs["highIsGood"] = ColumnSpec(False, None, False, set())
        dgmattribs["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        dataspec["dgmeffects"] = TableSpec({}, False)
        dgmeffects = dataspec["dgmeffects"].columns
        dgmeffects["effectID"] = ColumnSpec(True, None, False, set())
        dgmeffects["effectName"] = ColumnSpec(False, None, False, set())
        dgmeffects["description"] = ColumnSpec(False, None, False, set())
        dgmeffects["isOffensive"] = ColumnSpec(False, None, False, set())
        dgmeffects["isAssistance"] = ColumnSpec(False, None, False, set())
        dgmeffects["published"] = ColumnSpec(False, None, False, set())
        dataspec["dgmtypeattribs"] = TableSpec({}, False)
        dgmtypeattribs = dataspec["dgmtypeattribs"].columns
        dgmtypeattribs["typeID"] = ColumnSpec(True, "invtypes.typeID", True, set())
        dgmtypeattribs["attributeID"] = ColumnSpec(True, "dgmattribs.attributeID", False, set())
        dgmtypeattribs["value"] = ColumnSpec(False, None, False, set())
        dataspec["dgmtypeeffects"] = TableSpec({}, False)
        dgmtypeeffects = dataspec["dgmtypeeffects"].columns
        dgmtypeeffects["typeID"] = ColumnSpec(True, "invtypes.typeID", True, set())
        dgmtypeeffects["effectID"] = ColumnSpec(True, "dgmeffects.effectID", False, set())
        dataspec["eveunits"] = TableSpec({}, False)
        eveunits = dataspec["eveunits"].columns
        eveunits["unitID"] = ColumnSpec(True, None, False, set())
        eveunits["unitName"] = ColumnSpec(False, None, False, set())
        eveunits["displayName"] = ColumnSpec(False, None, False, set())
        dataspec["icons"] = TableSpec({}, False)
        icons = dataspec["icons"].columns
        icons["iconID"] = ColumnSpec(True, None, False, {0})
        icons["iconFile"] = ColumnSpec(False, None, False, set())
        icons["description"] = ColumnSpec(False, None, False, set())
        dataspec["invcategories"] = TableSpec({}, False)
        invcategories = dataspec["invcategories"].columns
        invcategories["categoryID"] = ColumnSpec(True, None, False, set())
        invcategories["categoryName"] = ColumnSpec(False, None, False, set())
        invcategories["description"] = ColumnSpec(False, None, False, set())
        invcategories["published"] = ColumnSpec(False, None, False, set())
        invcategories["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        dataspec["invgroups"] = TableSpec({}, False)
        invgroups = dataspec["invgroups"].columns
        invgroups["groupID"] = ColumnSpec(True, None, False, set())
        invgroups["categoryID"] = ColumnSpec(False, "invcategories.categoryID", False, set())
        invgroups["groupName"] = ColumnSpec(False, None, False, set())
        invgroups["published"] = ColumnSpec(False, None, False, set())
        invgroups["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        dataspec["invmarketgroups"] = TableSpec({}, False)
        invmarketgroups = dataspec["invmarketgroups"].columns
        invmarketgroups["parentGroupID"] = ColumnSpec(False, "invmarketgroups.marketGroupID", False, set())
        invmarketgroups["marketGroupID"] = ColumnSpec(True, None, False, set())
        invmarketgroups["marketGroupName"] = ColumnSpec(False, None, False, set())
        invmarketgroups["description"] = ColumnSpec(False, None, False, set())
        invmarketgroups["hasTypes"] = ColumnSpec(False, None, False, set())
        invmarketgroups["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        dataspec["invmetagroups"] = TableSpec({}, False)
        invmetagroups = dataspec["invmetagroups"].columns
        invmetagroups["metaGroupID"] = ColumnSpec(True, None, False, set())
        invmetagroups["metaGroupName"] = ColumnSpec(False, None, False, set())
        dataspec["invmetatypes"] = TableSpec({}, False)
        invmetatypes = dataspec["invmetatypes"].columns
        invmetatypes["typeID"] = ColumnSpec(True, "invtypes.typeID", False, set())
        invmetatypes["parentTypeID"] = ColumnSpec(False, "invtypes.typeID", False, set())
        invmetatypes["metaGroupID"] = ColumnSpec(False, "invmetagroups.metaGroupID", False, set())
        dataspec["invtypes"] = TableSpec({}, True)
        invtypes = dataspec["invtypes"].columns
        invtypes["typeID"] = ColumnSpec(True, None, False, set())
        invtypes["groupID"] = ColumnSpec(False, "invgroups.groupID", True, set())
        invtypes["typeName"] = ColumnSpec(False, None, True, set())
        invtypes["description"] = ColumnSpec(False, None, False, set())
        invtypes["mass"] = ColumnSpec(False, None, False, set())
        invtypes["volume"] = ColumnSpec(False, None, False, set())
        invtypes["capacity"] = ColumnSpec(False, None, False, set())
        invtypes["raceID"] = ColumnSpec(False, None, False, set())
        invtypes["published"] = ColumnSpec(False, None, False, set())
        invtypes["marketGroupID"] = ColumnSpec(False, "invmarketgroups.marketGroupID", False, set())
        invtypes["iconID"] = ColumnSpec(False, "icons.iconID", False, set())
        dataspec["metadata"] = TableSpec({}, False)
        metadata = dataspec["metadata"].columns
        metadata["fieldName"] = ColumnSpec(True, None, False, set())
        metadata["fieldValue"] = ColumnSpec(False, None, False, set())
        self.dbspec = dataspec
        self.__synch_dbinfo()
        strong_data = {}
        self.__process_manual_strongs(strong_data)
        self.__invtypes_pumping(strong_data)
        self.__metadata_pumping(strong_data)
        trashed_data = {}
        self.__autocleanup(strong_data, trashed_data, attrcat_attrid_map)
        self.__print_stats(trashed_data)
        return

    def __normalize_attrs(self):
        """Moves attributes defined in type table to type-attribs mapping table"""
        # Map which defines links between types table column names and attrIDs
        attr_map = {"radius": Attribute.radius,
                    "mass": Attribute.mass,
                    "volume": Attribute.volume,
                    "capacity": Attribute.capacity}
        # First, compose set of PK tuples which are already in target table
        typeattrs_table = self.evedb["dgmtypeattribs"]
        idx_typeattrs_typeid = typeattrs_table.index_by_name("typeID")
        idx_typeattrs_attrid = typeattrs_table.index_by_name("attributeID")
        idx_typeattrs_value = typeattrs_table.index_by_name("value")
        typeattrs_collen = len(typeattrs_table)
        existing_data = set()
        for datarow in typeattrs_table.datarows:
            existing_data.add((datarow[idx_typeattrs_typeid], datarow[idx_typeattrs_attrid]))
        # Now, start working with invtypes table
        types_table = self.evedb["invtypes"]
        idx_types_typeid = types_table.index_by_name("typeID")
        # Define replacement map, as we're going to update values in types table too
        type_replacements = {}
        # Flag which keeps track of any collision errors
        collisions = False
        # Go through each types table data row
        for datarow in types_table.datarows:
            mutablerow = list(datarow)
            for attrcolname in attr_map:
                # If such typeID-attributeID combination is already in typeattribs table,
                # don't do anything
                if (datarow[idx_types_typeid], attr_map[attrcolname]) in existing_data:
                    collisions = True
                    continue
                idx_types_attr = types_table.index_by_name(attrcolname)
                # If source attribute value is 0 or None, also skip such row
                attrval = datarow[idx_types_attr]
                if attrval in {0, None}:
                    continue
                # Initialize data row we're going to append to typeattrs table to 0 values
                typeattr_datarow = list(0 for _ in range(typeattrs_collen))
                # Fill it
                typeattr_datarow[idx_typeattrs_typeid] = datarow[idx_types_typeid]
                typeattr_datarow[idx_typeattrs_attrid] = attr_map[attrcolname]
                typeattr_datarow[idx_typeattrs_value] = attrval
                # And add it to target table
                typeattrs_table.datarows.add(tuple(typeattr_datarow))
                # Nullify data source in mutable row
                mutablerow[idx_types_attr] = 0.0
            # When operations on all attributes for given row are done, check if we
            # have made any changes to our mutable row
            replacementrow = tuple(mutablerow)
            if datarow != replacementrow:
                # If we did, fill in replacement map
                type_replacements[datarow] = replacementrow
        # Replace data in types table according to replacement map
        for datarow in type_replacements:
            types_table.datarows.remove(datarow)
            types_table.datarows.add(type_replacements[datarow])
        if collisions is True:
            print("  Key collisions detected during attribute normalization")
        return

    def __expression_idzing(self):
        """Convert all references in expression table to attributes, groups and types to IDs"""
        # Create replacement map which will store old and new data rows
        # Format: {current data row: replacement data row}
        replacement_map = {}
        # Set of entity field names which we're going to use
        idz_datas = (("dgmattribs", "attributeID", "attributeName", "expressionAttributeID", Operand.define_attribute),
                     ("invgroups", "groupID", "groupName", "expressionGroupID", Operand.define_group),
                     ("invtypes", "typeID", "typeName", "expressionTypeID", Operand.define_type))
        for idz_data in idz_datas:
            # First, we've got to compose name maps, as expressions can
            # reference using names
            entity_name_id = {}
            entity_name_collisions = set()
            entity_table = self.evedb[idz_data[0]]
            idx_entityid = entity_table.index_by_name(idz_data[1])
            idx_entityname = entity_table.index_by_name(idz_data[2])
            for datarow in entity_table.datarows:
                name = datarow[idx_entityname]
                if not name in entity_name_id:
                    entity_name_id[name] = datarow[idx_entityid]
                else:
                    entity_name_collisions.add(name)
                # Sometimes names with stripped white space symbols are used
                name_stripped = re.sub("\s", "", name)
                if not name_stripped in entity_name_id:
                    entity_name_id[name_stripped] = datarow[idx_entityid]
                else:
                    entity_name_collisions.add(name_stripped)
            # Get column indices for required columns in expression table
            exp_table = self.evedb["dgmexpressions"]
            idx_operand = exp_table.index_by_name("operandID")
            idx_expvalue = exp_table.index_by_name("expressionValue")
            idx_expentity = exp_table.index_by_name(idz_data[3])
            for datarow in exp_table.datarows:
                operand = datarow[idx_operand]
                # Check if we're dealing with the operand referring entity
                # we're working with
                if operand == idz_data[4]:
                    entity = datarow[idx_expentity]
                    val = datarow[idx_expvalue]
                    # Check that actual reference to entity type being checked
                    # is absent, but there's some expression value
                    if entity is None and val in entity_name_id:
                        if val in entity_name_collisions:
                            print("  Warning: use of colliding {0} {1} detected, expect errors".format(idz_data[2], val))
                        mutablerow = list(datarow)
                        mutablerow[idx_expentity] = entity_name_id[val]
                        mutablerow[idx_expvalue] = None
                        replacementrow = tuple(mutablerow)
                        replacement_map[datarow] = replacementrow
        # Do actual replacements
        for datarow in replacement_map:
            exp_table.datarows.remove(datarow)
            exp_table.datarows.add(replacement_map[datarow])
        return

    def __combine_translations(self):
        """Place translations for all languages into single table"""
        # Format: {langID: language table}
        langid_table_map = {}
        # Go through all tables and pick tables with actual translation data
        for table in self.evedb:
            match = re.match("^trntexts_(.+)", table.name)
            if match is None:
                continue
            langID = match.group(1)
            langid_table_map[langID] = table
        # Container for unified data
        # Format: {textID: {langID: text}}
        dictrows = {}
        # Fill it with data
        for langID, table in langid_table_map.iteritems():
            for textID, text in table.datarows:
                if not textID in dictrows:
                    dictrows[textID] = {}
                dictrows[textID][langID] = text
            # And remove source tables
            self.evedb.remove(table)
        # Compose list of headers for new table
        headers = []
        for langID in langid_table_map.iterkeys():
            if not langID in headers:
                headers.append(langID)
        # Sort language IDs alphabetically
        headers.sort()
        # And prepend column which will be PK
        headers.insert(0, "textID")
        # Create table
        table = self.evedb.add_table("trntexts")
        # Fill it with columns
        for header in headers:
            table.add_column(header)
        # And actual data rows
        for textID, dictrow in dictrows.iteritems():
            dictrow["textID"] = textID
            datarow = tuple(dictrow.get(header) for header in headers)
            table.datarows.add(datarow)
        return

    def __synch_dbinfo(self):
        """Synchronize data between data specification and actual database structure"""
        evedb = self.evedb
        # Just error flag, used for user's convenience
        specerrors = False
        # Detect non-existing tables
        tabnames_dbspec = set(self.dbspec.iterkeys())
        tabnames_evedb = set(table.name for table in evedb)
        tab404 = tabnames_dbspec.difference(tabnames_evedb)
        # If we found any
        if len(tab404) > 0:
            # Remove them from specification container
            for tabname in tab404:
                del self.dbspec[tabname]
            # And inform about it
            plu = "" if len(tab404) == 1 else "s"
            tab404names = ", ".join(sorted(tab404))
            print("  Unable to find specified table{0}: {1}".format(plu, tab404names))
            # Set error flag to True
            specerrors = True
        # Get set of tables to be removed from actual data and get rid of them
        toremove = tabnames_evedb.difference(tabnames_dbspec)
        for tabname in toremove:
            evedb.remove(evedb[tabname])
        # Cycle through remaining tables
        # Sort them for alphabetic table name sorting, this is done for pretty-print
        # in case of any errors (doesn't matter otherwise)
        for tabname in sorted(self.dbspec.iterkeys()):
            table = evedb[tabname]
            colnames_evedb = set(col.name for col in table)
            colnames_dbspec = set(self.dbspec[tabname].columns.iterkeys())
            # Detect non-existing columns
            col404 = colnames_dbspec.difference(colnames_evedb)
            # If we've got such columns
            if len(col404) > 0:
                # Remove them from specification
                for col in col404:
                    del self.dbspec[tabname].columns[col]
                # Tell user about it
                plu = "" if len(col404) == 1 else "s"
                col404names = ", ".join(sorted(col404))
                print("  Unable to find specified column{0} for table {1}: {2}".format(plu, tabname, col404names))
                # Set error flag to True
                specerrors = True
            # Finally, get rid of unneeded columns in actual data structure
            toremove = colnames_evedb.difference(colnames_dbspec)
            problems = table.remove_columns(toremove)
            # If we had any errors during column  removal, set error flag
            if problems is True:
                specerrors = True

        # Define data format for remaining data
        preproc = Preprocessor(evedb)
        preproc.run()

        # Check if autodetected PKs match specified manually
        for table in sorted(evedb, key=lambda table: table.name):
            pknames_evedb = set(column.name for column in table.get_pks())
            pknames_dbspec = set(colitem[0] for colitem in filter(lambda colitem: colitem[1].pk is True, self.dbspec[table.name].columns.iteritems()))
            # If they match, don't attempt to do anything and skip to next table
            if pknames_evedb == pknames_dbspec:
                continue
            # Else, check if specified manually columns can be a key
            validpks = True
            pkindices = []
            for pkname in pknames_dbspec:
                pkcolumn = table[pkname]
                # All data must be not-null
                if pkcolumn.notnull is not True:
                    validpks = False
                    break
                # Gather indices of PKed columns
                pkindices.append(table.index(pkcolumn))
            if validpks is False:
                print("  PK for table {0} contains null values, using autodetected PKs".format(table.name))
                specerrors = True
                continue
            keys = set()
            # Check if data set for given PKs is unique
            for datarow in table.datarows:
                key = tuple(datarow[idx] for idx in pkindices)
                if key in keys:
                    validpks = False
                    break
                keys.add(key)
            if validpks is False:
                print("  PK for table {0} contains non-distinct values, using autodetected PKs".format(table.name))
                specerrors = True
                continue
            # If all checks were passed, reassign PK flags for columns
            for column in table:
                column.pk = True if column.name in pknames_dbspec else False

        # Fill foreign key references for all columns according to specification
        for table in evedb:
            for column in table:
                # Get FK specification string
                fkspec = self.dbspec[table.name].columns[column.name].fk
                # If it's None, ignore current column
                if fkspec is None:
                    continue
                # Source data column must be integer
                if column.datatype != DataType.integer:
                    print("  Non-integer column {0}.{1} has foreign key reference".format(table.name, column.name))
                    specerrors = True
                    continue
                fkspec = fkspec.split(".")
                # FK specification string must be in table.column format
                if len(fkspec) != 2:
                    print("  Foreign key reference of {0}.{1} is malformed".format(table.name, column.name))
                    specerrors = True
                    continue
                fktabname = fkspec[0]
                fkcolname = fkspec[1]
                # FK target must exist
                tabnames_evedb = set(table.name for table in evedb)
                if not fktabname in tabnames_evedb or evedb[fktabname].get(fkcolname) is None:
                    print("  Unable to find foreign key target for {0}.{1} ({2}.{3})".format(table.name, column.name, fktabname, fkcolname))
                    specerrors = True
                    continue
                fktable = evedb[fktabname]
                fkcolumn = fktable.get(fkcolname)
                # FK target must be PK
                if fkcolumn.pk is not True:
                    print("  Foreign key target for {0}.{1} ({2}.{3}) is not primary key".format(table.name, column.name, fktabname, fkcolname))
                    specerrors = True
                    continue
                # FK target table must have no other PKs besides targeted
                if len(fktable.get_pks()) != 1:
                    print("  Foreign key target for {0}.{1} ({2}.{3}) is not the only primary key in table".format(table.name, column.name, fktabname, fkcolname))
                    specerrors = True
                    continue
                # Store FK value in column field
                column.fk = "{0}.{1}".format(fktable.name, fkcolumn.name)

        # Set index flags for all appropriate columns
        for tabname in sorted(self.dbspec.iterkeys()):
            for colname in self.dbspec[tabname].columns:
                idxize = self.dbspec[tabname].columns[colname].index
                if idxize in (True, False):
                    self.evedb[tabname][colname].index = idxize
                # Print error on unexpected values
                else:
                    print("  Corrupted index data for {0}.{1}".format(tabname, colname))

        # Print reminder in case of any errors
        if specerrors is True:
            print("  Please revise data specification")

    def __process_manual_strongs(self, strong_data):
        """Add manually specified strong data to internal temporary storage"""
        # Go through all tables in specifications
        for tabname in self.dbspec:
            table = self.evedb[tabname]
            # Container for rows of given table which we're going to
            # mark as strong
            rows2pump = set()
            # All their columns
            for colname in self.dbspec[tabname].columns:
                # Check strong values section
                strong_vals = self.dbspec[tabname].columns[colname].strongvals
                # If it's empty, go on
                if len(strong_vals) == 0:
                    continue
                # Get index of column in question
                colidx = table.index_by_name(colname)
                # Go through data rows and see which match to our criterion
                for datarow in table.datarows:
                    # If row matches, add it to strong data set
                    if datarow[colidx] in strong_vals:
                        rows2pump.add(datarow)
            self.__pump_data(table, rows2pump, strong_data)
        return

    def __invtypes_pumping(self, strong_data):
        """Mark some hardcoded invtypes as strong"""
        # Set with categoryIDs of published items we want to keep
        strong_categories = {Category.ship, Category.module, Category.charge,
                             Category.skill, Category.drone, Category.implant,
                             Category.subsystem}
        # Set with groupIDs of published items we want to keep
        strong_groups = {Group.effect_beacon}
        # Get indices of group and category columns in group table
        group_table = self.evedb["invgroups"]
        idx_groupid = group_table.index_by_name("groupID")
        idx_categoryid = group_table.index_by_name("categoryID")
        # Go through table data, filling valid groups set according to valid categories
        for datarow in group_table.datarows:
            if datarow[idx_categoryid] in strong_categories:
                strong_groups.add(datarow[idx_groupid])
        # Get typeIDs of items we're going to pump
        type_table = self.evedb["invtypes"]
        idx_groupid = type_table.index_by_name("groupID")
        idx_published = type_table.index_by_name("published")
        # Set-container for strong types
        rows2pump = set()
        for datarow in type_table.datarows:
            groupid = datarow[idx_groupid]
            published = bool(datarow[idx_published])
            if groupid in strong_groups and published is True:
                rows2pump.add(datarow)
        self.__pump_data(type_table, rows2pump, strong_data)
        return

    def __metadata_pumping(self, strong_data):
        """Protect metadata table from removal"""
        # Set with categoryIDs we want to keep
        metadata_table = self.evedb["metadata"]
        self.__pump_data(metadata_table, metadata_table.datarows, strong_data)
        return

    def __autocleanup(self, strong_data, trashed_data, attrcat_attrid_map):
        """Define auto cleanup workflow"""
        # Our first step would be to clean non-strong data
        self.__kill_weak(strong_data, trashed_data)
        # Detect table types, as we'll need them for proper data restore
        # process
        tabletypes = self.__detect_tabletypes()
        # Put all FK links into single dictionary
        src_fk_tgt, tgt_fk_src = self.__make_fk_links()
        # Now, start reanimating all related data in cycle
        # Set flag to True for first cycle
        changed = True
        while(changed):
            # Instantly reset to False, any changes to data should set it back
            changed = False
            changed = self.__reanimate_aux_friends(tabletypes, src_fk_tgt, trashed_data, changed)
            changed = self.__reestablish_broken_relationships(src_fk_tgt, tgt_fk_src, trashed_data, attrcat_attrid_map, changed)
        # Here, we may want to add cyclic (like in previous step):
        # 1) Removal of entries with still-broken FK relationships (including conditional attribute value references)
        # 2) Removal of data with no references to it
        return

    def __kill_weak(self, strong_data, trashed_data):
        """Trash all data which isn't marked as strong"""
        # Go through all tables
        for table in self.evedb:
            rows2trash = set()
            strongrows = strong_data.get(table.name)
            # If it doesn't contain strong rows, kill all data
            if strongrows is None:
                rows2trash.update(table.datarows)
            # Else, filter out our strong rows
            else:
                rows2trash.update(table.datarows.difference(strongrows))
            # Finally, trash all data rows
            self.__trash_data(table, rows2trash, trashed_data)
        return

    def __detect_tabletypes(self):
        """Based on PK and FK data, detects table type"""
        # Create container holding our table type specifications
        type_map = {}
        for table in self.evedb:
            # We will judge basing on PK number as one of the factos
            pks = len(table.get_pks())
            # If there's no PKs at all or 2+ PKs, then table is auxiliary
            if pks > 1 or pks == 0:
                type_map[table.name] = TableType.auxiliary
                continue
            # Even if there's single PK, but it references something else -
            # it means that table contents contain complementary data, thus table is
            # auxiliary too
            for column in table:
                if column.pk is True and column.fk is not None:
                    type_map[table.name] = TableType.auxiliary
                    break
            # Additional check to avoid going further, if we already detected
            # type of current table
            if table.name in type_map:
                continue
            # Else, type is base
            type_map[table.name] = TableType.base
        return type_map

    def __make_fk_links(self):
        """Form dictionary to store links between tables in convenient form"""
        # 1:1 source-target relation
        # {source table: {source column: (target table, target column)}}
        src_fk_tgt = {}
        # 1:many target-source relation
        # {target table: {target column: {(source table, source column)}}}
        tgt_fk_src = {}
        # Go through all tables to fill map
        for src_table in self.evedb:
            for src_column in src_table:
                # Columns with no FK are no interest for us
                if src_column.fk is None:
                    continue
                tgt_tabname, tgt_colname = src_column.fk.split(".")
                tgt_table = self.evedb[tgt_tabname]
                tgt_column = tgt_table[tgt_colname]
                # Fill source-target map
                if not src_table.name in src_fk_tgt:
                    src_fk_tgt[src_table.name] = {}
                src_fk_tgt[src_table.name][src_column.name] = (tgt_table.name, tgt_column.name)
                # And target-source
                if not tgt_table.name in tgt_fk_src:
                    tgt_fk_src[tgt_table.name] = {}
                if not tgt_column.name in tgt_fk_src[tgt_table.name]:
                    tgt_fk_src[tgt_table.name][tgt_column.name] = set()
                tgt_fk_src[tgt_table.name][tgt_column.name].add((src_table.name, src_column.name))
        return src_fk_tgt, tgt_fk_src


    def __reanimate_aux_friends(self, tabletypes, src_fk_tgt, trashed_data, changed):
        """Restore auxiliary data which is related to data left in the database"""
        # Container for column data, for data re-use
        # Format: {"table.column": {data}}
        coldata = {}
        # Fill it with data, for columns which are referenced by FKs
        for src_tabname in src_fk_tgt:
            # We won't need data for any source tables besides
            # auxiliary ones, so skip all other types
            if tabletypes[src_tabname] != TableType.auxiliary:
                continue
            # Go through all column-FKs in auxiliary table
            for src_colname in src_fk_tgt[src_tabname]:
                # Pick FK target and form full textual specification
                tgt_tabname, tgt_colname = src_fk_tgt[src_tabname][src_colname]
                # We're planning to restore auxiliary data only for
                # strong tables, so skip all others
                tgt_strength = self.dbspec[tgt_tabname].strong
                if tgt_strength is not True:
                    continue
                tgt_spec = "{0}.{1}".format(tgt_tabname, tgt_colname)
                # Get data for target column into single set, but only if it's
                # not yet there
                if not tgt_spec in coldata:
                    tgt_dataset = self.evedb[tgt_tabname].get_columndataset(tgt_colname)
                    coldata[tgt_spec] = tgt_dataset
        # Now, to the actual restore process
        for src_tabname in src_fk_tgt:
            # Skip all non-auxiliary tables
            if tabletypes[src_tabname] != TableType.auxiliary:
                continue
            src_table = self.evedb[src_tabname]
            # Container for data we're going to restore
            rows2restore = set()
            # Go through all FK columns of out table
            for src_colname in src_fk_tgt[src_tabname]:
                tgt_tabname, tgt_colname = src_fk_tgt[src_tabname][src_colname]
                # Skip non-strong target tables
                tgt_strength = self.dbspec[tgt_tabname].strong
                if tgt_strength is not True:
                    continue
                tgt_spec = "{0}.{1}".format(tgt_tabname, tgt_colname)
                src_colidx = src_table.index_by_name(src_colname)
                # For each, check all thrashed data
                for datarow in trashed_data[src_tabname]:
                    src_val = datarow[src_colidx]
                    # If there's no value or it keeps zero, skip this row
                    if src_val in {0, None}:
                        continue
                    # If any of such rows refers existing target row,
                    # mark it as to-be-restored
                    if src_val in coldata[tgt_spec]:
                        rows2restore.add(datarow)
            # Restore rows
            self.__restore_data(src_table, rows2restore, trashed_data)
            # If we actually had something to restore, let others know about it
            if len(rows2restore) > 0:
                changed = True
        return changed

    def __reestablish_broken_relationships(self, src_fk_tgt, tgt_fk_src, trashed_data, attrcat_attrid_map, changed):
        """Restore rows targeted by FKs of actual data"""
        # Container for column data, for data re-use
        # Format: {"table.column": {data}}
        coldata = {}
        # Fill it with data, for columns which are FKs
        for src_tabname in src_fk_tgt:
            # Go through all column-FKs in auxiliary table
            for src_colname in src_fk_tgt[src_tabname]:
                # Pick FK target and form full textual specification
                src_spec = "{0}.{1}".format(src_tabname, src_colname)
                # Get data for source column into single set
                src_dataset = self.evedb[src_tabname].get_columndataset(src_colname)
                # None and zero values are not actual references according to
                # CCP scheme, so get rid of them
                src_dataset.difference_update({0, None})
                coldata[src_spec] = src_dataset
        # Restore broken plain references; go through all target tables and columns
        for tgt_tabname in tgt_fk_src:
            tgt_table = self.evedb[tgt_tabname]
            # Set-container for rows to be restored
            rows2restore = set()
            for tgt_colname in tgt_fk_src[tgt_tabname]:
                # Values which reference given target column are collected here
                src_vals = set()
                # Use our pre-gathered column data set as data source
                for src_tabname, src_colname in tgt_fk_src[tgt_tabname][tgt_colname]:
                    src_spec = "{0}.{1}".format(src_tabname, src_colname)
                    src_vals.update(coldata[src_spec])
                # Finally, go through rows of removed data and mark it as to-be-restored
                # if match happens
                tgt_colidx = tgt_table.index_by_name(tgt_colname)
                for datarow in trashed_data[tgt_tabname]:
                    tgt_val = datarow[tgt_colidx]
                    if tgt_val in src_vals:
                        rows2restore.add(datarow)
            # Actual data restore for given table
            self.__restore_data(tgt_table, rows2restore, trashed_data)
            if len(rows2restore) > 0:
                changed = True
        # Restore broken conditional references; first, grab their source values
        special_attrval_links = self.__define_attrvalue_relationships(attrcat_attrid_map)
        # Then follow almost the same approach
        for tgt_tabname in special_attrval_links:
            tgt_table = self.evedb[tgt_tabname]
            rows2restore = set()
            for tgt_colname in special_attrval_links[tgt_tabname]:
                # Except for the fact that we already have our data at hand and can use it
                # without additional gathering
                src_vals = special_attrval_links[tgt_tabname][tgt_colname]
                tgt_colidx = tgt_table.index_by_name(tgt_colname)
                for datarow in trashed_data[tgt_tabname]:
                    tgt_val = datarow[tgt_colidx]
                    if tgt_val in src_vals:
                        rows2restore.add(datarow)
            # Actually restore rows
            self.__restore_data(tgt_table, rows2restore, trashed_data)
            if len(rows2restore) > 0:
                changed = True
        return changed

    def __define_attrvalue_relationships_hamster(self):
        """Hamster some data before it gets removed, it's needed for primary method"""
        # Format: {attrCategory: {attrID}}
        attrcat_attrid_map = {}
        attr_table = self.evedb["dgmattribs"]
        idx_attrid = attr_table.index_by_name("attributeID")
        idx_attrcat = attr_table.index_by_name("attributeCategory")
        for datarow in attr_table.datarows:
            attrcat = datarow[idx_attrcat]
            if not attrcat in attrcat_attrid_map:
                attrcat_attrid_map[attrcat] = set()
            attrcat_attrid_map[attrcat].add(datarow[idx_attrid])
        return attrcat_attrid_map

    def __define_attrvalue_relationships(self, attrcat_attrid_map):
        """
        Provide additional data of what we need to keep in the database, namely -
        under certain conditions attribute values refer other entities, which we're
        better to keep.
        """
        # Storage for values which actually refer something
        # Format: {table name: {column name: values to restore}}
        special_attrval_links = {}
        # Get indices to work with data in dgmtypeattribs table
        typeattrs_table = self.evedb["dgmtypeattribs"]
        idx_attrid = typeattrs_table.index_by_name("attributeID")
        idx_value = typeattrs_table.index_by_name("value")
        # Some high-level access instructions, what to restore
        conditional_links = {(AttributeCategory.define_attribute, "dgmattribs", "attributeID"),
                             (AttributeCategory.define_group, "invgroups", "groupID"),
                             (AttributeCategory.define_type, "invtypes", "typeID")}
        # Go through each of them
        for entity_attrcat, entity_tabname, entity_colname in conditional_links:
            # Container for attribute IDs which reference corresponding entity
            attrs_entity = attrcat_attrid_map[entity_attrcat]
            # Container for IDs of entities we're going to restore
            referenced_entities = set()
            # Cycle through data rows and see if we get attribute ID match
            for datarow in typeattrs_table.datarows:
                # If we do, write down ID of entity to corresponding set
                if datarow[idx_attrid] in attrs_entity:
                    value = datarow[idx_value]
                    referenced_entities.add(int(value))
            referenced_entities.difference_update({0, None})
            # Store data to dictionary
            if not entity_tabname in special_attrval_links:
                special_attrval_links[entity_tabname] = {}
            special_attrval_links[entity_tabname][entity_colname] = referenced_entities
        return special_attrval_links

    def __print_stats(self, trashed_data):
        """Print statistics about removed data"""
        # Print some statistics
        for tabname in sorted(trashed_data):
            # Get set with removed data
            removed_data = trashed_data.get(tabname)
            removedrows = len(removed_data)
            # If set is empty, don't do anything
            if removedrows == 0:
                continue
            table = self.evedb[tabname]
            # Calculate total number of data rows we had in table
            totalrows = len(table.datarows) + removedrows
            # Print jobs
            plu = "" if removedrows == 1 else "s"
            perc = 100.0 * removedrows / totalrows
            print("  Table {0} cleaned: {1} row{2} ({3:.1f}%) removed".format(tabname, removedrows, plu, perc))
        return

    def __pump_data(self, table, datarows, strong_data):
        """Mark data rows as strong"""
        # Check if we got anything useful, bail if we didn't
        if len(datarows) == 0:
            return
        # Create sub-set for table if it doesn't have it yet
        if not table.name in strong_data:
            strong_data[table.name] = set()
        # Actually add data rows
        strong_data[table.name].update(datarows)
        return

    def __trash_data(self, table, datarows, trashed_data):
        """Mark data as removed"""
        # If no data was passed, bail - as usual
        if len(datarows) == 0:
            return
        # Create subset if it's not yet there
        if not table.name in trashed_data:
            trashed_data[table.name] = set()
        totrash = table.datarows.intersection(datarows)
        # Update both trashed data and source data
        trashed_data[table.name].update(totrash)
        table.datarows.difference_update(totrash)
        return

    def __restore_data(self, table, datarows, trashed_data):
        """Mark data as actual, if it is trashed"""
        # If no data was passed, bail - as usual
        if len(datarows) == 0:
            return
        torestore = trashed_data[table.name].intersection(datarows)
        # Update both trashed data and source data
        table.datarows.update(torestore)
        trashed_data[table.name].difference_update(torestore)
        return
