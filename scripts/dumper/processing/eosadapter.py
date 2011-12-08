#!/usr/bin/env python
#===============================================================================
# Copyright (C) 2010-2011 Anton Vorobyov
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

import const

# Auxiliary named tuples for use with custom database structure specification
TableSpec = collections.namedtuple("TableSpec", ("columns", "strong"))
ColumnSpec = collections.namedtuple("ColumnSpec", ("fk", "index", "strongvals"))

class EosAdapter(object):
    """
    Adapt data to use in Eos before dumping
    """
    def __init__(self, tables):
        self.tables = tables

    def run(self):
        """Control database refactoring workflow"""
        print("Refactoring database for Eos")
        self.dbspec = self.__get_dbspec()
        # Delete malformed entries in both structures; also, fill actual data
        # with additional flags taken from custom data specification
        self.__synch_dbinfo()
        # Transform literal references to IDs in expressions table
        self.__expression_idzing()
        # Create data structure for removed data, we need it for proper resulting
        # statistics and in case if we want to put something back
        # Format: {table name: {data row: removal reason}}
        self.removed_data = {}
        for tabname in self.tables:
            self.removed_data[tabname] = {}
        # Filter out data for invtypes table
        self.__manual_filter_invtypes()
        # Container to store signs of so-called strong data, such rows are immune to removal
        # Format: {table name: {column index: {exception values}}
        self.strong_data = {}
        # Fill it with manually specified data
        self.__process_manual_strongs()
        # Automatically clean up broken data
        self.__cyclic_autocleanup()
        # Put some data back
        self.__restore_surface_attrrefereces()
        # Print some statistics to know what has been cleaned
        self.__print_stats()

    def __get_dbspec(self):
        """Return specification of data Eos needs"""
        dataspec = {}

        dataspec["dgmattribs"] = TableSpec({}, False)
        dgmattribs = dataspec["dgmattribs"].columns
        dgmattribs["attributeID"] = ColumnSpec(None, False, None)
        dgmattribs["attributeName"] = ColumnSpec(None, False, {"radius", "mass", "volume", "capacity"})
        dgmattribs["attributeCategory"] = ColumnSpec(None, False, None)
        #dgmattribs["description"] = ColumnSpec(None, False, None)
        dgmattribs["maxAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        #dgmattribs["chargeRechargeTimeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmattribs["defaultValue"] = ColumnSpec(None, False, None)
        dgmattribs["published"] = ColumnSpec(None, False, None)
        dgmattribs["displayName"] = ColumnSpec(None, False, None)
        dgmattribs["unitID"] = ColumnSpec("eveunits.unitID", False, None)
        dgmattribs["stackable"] = ColumnSpec(None, False, None)
        dgmattribs["highIsGood"] = ColumnSpec(None, False, None)
        #dgmattribs["categoryID"] = ColumnSpec(None, False, None)
        dgmattribs["iconID"] = ColumnSpec("icons.iconID", False, None)

        dataspec["dgmeffects"] = TableSpec({}, False)
        dgmeffects = dataspec["dgmeffects"].columns
        dgmeffects["effectID"] = ColumnSpec(None, False, None)
        dgmeffects["effectName"] = ColumnSpec(None, False, None)
        dgmeffects["preExpression"] = ColumnSpec("dgmexpressions.expressionID", False, None)
        dgmeffects["postExpression"] = ColumnSpec("dgmexpressions.expressionID", False, None)
        dgmeffects["effectCategory"] = ColumnSpec(None, False, None)
        #dgmeffects["description"] = ColumnSpec(None, False, None)
        dgmeffects["isOffensive"] = ColumnSpec(None, False, None)
        dgmeffects["isAssistance"] = ColumnSpec(None, False, None)
        dgmeffects["durationAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmeffects["trackingSpeedAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmeffects["dischargeAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmeffects["rangeAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmeffects["falloffAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        #dgmeffects["published"] = ColumnSpec(None, False, None)
        dgmeffects["displayName"] = ColumnSpec(None, False, None)
        #dgmeffects["isWarpSafe"] = ColumnSpec(None, False, None)
        dgmeffects["fittingUsageChanceAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmeffects["iconID"] = ColumnSpec("icons.iconID", False, None)

        dataspec["dgmexpressions"] = TableSpec({}, False)
        dgmexpressions = dataspec["dgmexpressions"].columns
        dgmexpressions["expressionID"] = ColumnSpec(None, False, None)
        dgmexpressions["operandID"] = ColumnSpec(None, False, None)
        dgmexpressions["arg1"] = ColumnSpec("dgmexpressions.expressionID", False, None)
        dgmexpressions["arg2"] = ColumnSpec("dgmexpressions.expressionID", False, None)
        dgmexpressions["expressionValue"] = ColumnSpec(None, False, None)
        dgmexpressions["expressionTypeID"] = ColumnSpec("invtypes.typeID", False, None)
        dgmexpressions["expressionGroupID"] = ColumnSpec("invgroups.groupID", False, None)
        dgmexpressions["expressionAttributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)

        dataspec["dgmtypeattribs"] = TableSpec({}, False)
        dgmtypeattribs = dataspec["dgmtypeattribs"].columns
        dgmtypeattribs["typeID"] = ColumnSpec("invtypes.typeID", False, None)
        dgmtypeattribs["attributeID"] = ColumnSpec("dgmattribs.attributeID", False, None)
        dgmtypeattribs["value"] = ColumnSpec(None, False, None)

        dataspec["dgmtypeeffects"] = TableSpec({}, False)
        dgmtypeeffects = dataspec["dgmtypeeffects"].columns
        dgmtypeeffects["typeID"] = ColumnSpec("invtypes.typeID", False, None)
        dgmtypeeffects["effectID"] = ColumnSpec("dgmeffects.effectID", False, None)
        dgmtypeeffects["isDefault"] = ColumnSpec(None, False, None)

        dataspec["eveunits"] = TableSpec({}, False)
        eveunits = dataspec["eveunits"].columns
        eveunits["unitID"] = ColumnSpec(None, False, None)
        #eveunits["unitName"] = ColumnSpec(None, False, None)
        eveunits["displayName"] = ColumnSpec(None, False, None)
        #eveunits["description"] = ColumnSpec(None, False, None)

        dataspec["icons"] = TableSpec({}, False)
        icons = dataspec["icons"].columns
        icons["iconID"] = ColumnSpec(None, False, None)
        icons["iconFile"] = ColumnSpec(None, False, None)
        #icons["description"] = ColumnSpec(None, False, None)
        #icons["iconType"] = ColumnSpec(None, False, None)

        dataspec["invcategories"] = TableSpec({}, False)
        invcategories = dataspec["invcategories"].columns
        invcategories["categoryID"] = ColumnSpec(None, False, None)
        invcategories["categoryName"] = ColumnSpec(None, False, None)
        #invcategories["description"] = ColumnSpec(None, False, None)
        #invcategories["published"] = ColumnSpec(None, False, None)
        #invcategories["iconID"] = ColumnSpec("icons.iconID", False, None)

        dataspec["invgroups"] = TableSpec({}, False)
        invgroups = dataspec["invgroups"].columns
        invgroups["groupID"] = ColumnSpec(None, False, None)
        invgroups["categoryID"] = ColumnSpec("invcategories.categoryID", False, None)
        invgroups["groupName"] = ColumnSpec(None, False, None)
        invgroups["fittableNonSingleton"] = ColumnSpec(None, False, None)
        #invgroups["description"] = ColumnSpec(None, False, None)
        invgroups["published"] = ColumnSpec(None, False, None)
        invgroups["iconID"] = ColumnSpec("icons.iconID", False, None)

        dataspec["invmarketgroups"] = TableSpec({}, False)
        invmarketgroups = dataspec["invmarketgroups"].columns
        invmarketgroups["parentGroupID"] = ColumnSpec("invmarketgroups.marketGroupID", False, None)
        invmarketgroups["marketGroupID"] = ColumnSpec(None, False, None)
        invmarketgroups["marketGroupName"] = ColumnSpec(None, False, None)
        #invmarketgroups["description"] = ColumnSpec(None, False, None)
        invmarketgroups["hasTypes"] = ColumnSpec(None, False, None)
        invmarketgroups["iconID"] = ColumnSpec("icons.iconID", False, None)

        dataspec["invmetagroups"] = TableSpec({}, False)
        invmetagroups = dataspec["invmetagroups"].columns
        invmetagroups["metaGroupID"] = ColumnSpec(None, False, None)
        invmetagroups["metaGroupName"] = ColumnSpec(None, False, None)
        #invmetagroups["description"] = ColumnSpec(None, False, None)

        dataspec["invmetatypes"] = TableSpec({}, False)
        invmetatypes = dataspec["invmetatypes"].columns
        invmetatypes["typeID"] = ColumnSpec("invtypes.typeID", False, None)
        invmetatypes["parentTypeID"] = ColumnSpec("invtypes.typeID", False, None)
        invmetatypes["metaGroupID"] = ColumnSpec("invmetagroups.metaGroupID", False, None)

        dataspec["invtypes"] = TableSpec({}, True)
        invtypes = dataspec["invtypes"].columns
        invtypes["typeID"] = ColumnSpec(None, False, None)
        invtypes["groupID"] = ColumnSpec("invgroups.groupID", False, None)
        invtypes["typeName"] = ColumnSpec(None, False, None)
        invtypes["description"] = ColumnSpec(None, False, None)
        invtypes["radius"] = ColumnSpec(None, False, None)
        invtypes["mass"] = ColumnSpec(None, False, None)
        invtypes["volume"] = ColumnSpec(None, False, None)
        invtypes["capacity"] = ColumnSpec(None, False, None)
        invtypes["raceID"] = ColumnSpec(None, False, None)
        invtypes["published"] = ColumnSpec(None, False, None)
        invtypes["marketGroupID"] = ColumnSpec("invmarketgroups.marketGroupID", False, None)
        invtypes["iconID"] = ColumnSpec("icons.iconID", False, None)

        dataspec["metadata"] = TableSpec({}, False)
        metadata = dataspec["metadata"].columns
        metadata["fieldName"] = ColumnSpec(None, False, None)
        metadata["fieldValue"] = ColumnSpec(None, False, None)

        return dataspec

    def __synch_dbinfo(self):
        """Synchronize data between data specification and actual database structure"""
        # Just error flag, used for user's convenience
        specerrors = False
        # Detect non-existing tables
        tab404 = set(self.dbspec.iterkeys()).difference(self.tables.iterkeys())
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
        toremove = set(self.tables.iterkeys()).difference(set(self.dbspec.iterkeys()))
        for tabname in toremove:
            del self.tables[tabname]
        # Cycle through remaining tables
        # Sort them for alphabetic table name sorting, this is done for pretty-print
        # in case of any errors (doesn't matter otherwise)
        for tabname in sorted(self.dbspec.iterkeys()):
            table = self.tables[tabname]
            actcolnames = set(col.name for col in table.columns)
            specolnames = set(self.dbspec[tabname].columns.iterkeys())
            # Detect non-existing columns
            col404 = specolnames.difference(actcolnames)
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
            toremove = actcolnames.difference(self.dbspec[tabname].columns.iterkeys())
            problems = table.removecolumns(toremove)
            # If we had any errors during column  removal, set error flag
            if problems is True:
                specerrors = True

        # Fill foreign key references for all columns according to specification
        # As our data/specification structures are now 'synchronized', we can go
        # through any of them - here we picked data as it's faster and more convenient
        for tabname in self.tables:
            table = self.tables[tabname]
            for column in table.columns:
                # Get FK specification string
                fkspec = self.dbspec[table.name].columns[column.name].fk
                # If it's None, ignore current column
                if fkspec is None:
                    continue
                # Source data column must be integer
                if column.datatype != const.type_INT:
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
                if not fktabname in self.tables or self.tables[fktabname].getcolumn(fkcolname) is None:
                    print("  Unable to find foreign key target for {0}.{1} ({2}.{3})".format(table.name, column.name, fktabname, fkcolname))
                    specerrors = True
                    continue
                fktable = self.tables[fktabname]
                fkcolumn = fktable.getcolumn(fkcolname)
                # FK target must be PK
                if fkcolumn.pk is not True:
                    print("  Foreign key target for {0}.{1} ({2}.{3}) is not primary key".format(table.name, column.name, fktabname, fkcolname))
                    specerrors = True
                    continue
                # FK target table must have no other PKs besides targeted
                if len(fktable.getpks()) != 1:
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
                    self.tables[tabname].getcolumn(colname).index = idxize
                # Print error on unexpected values
                else:
                    print("  Corrupted index data for {0}.{1}".format(tabname, colname))

        # Print reminder in case of any errors
        if specerrors is True:
            print("  Please revise data specification")

    def __expression_idzing(self):
        """Convert all references in expression table to attributes, groups and types to IDs"""
        # First, we've got to compose name maps, as expressions can
        # reference using names (sometimes with white space symbols stripped)
        # Do it for attributes
        attr_name_id = {}
        attr_name_collisions = set()
        attr_table = self.tables["dgmattribs"]
        idx_attrid = attr_table.getcolumnidx("attributeID")
        idx_attrname = attr_table.getcolumnidx("attributeName")
        for datarow in attr_table.datarows:
            name = datarow[idx_attrname]
            if not name in attr_name_id:
                attr_name_id[name] = datarow[idx_attrid]
            else:
                attr_name_collisions.add(name)
            name_stripped = re.sub("\s", "", name)
            if not name_stripped in attr_name_id:
                attr_name_id[name_stripped] = datarow[idx_attrid]
            else:
                attr_name_collisions.add(name_stripped)
        # For groups
        group_name_id = {}
        group_name_collisions = set()
        group_table = self.tables["invgroups"]
        idx_groupid = group_table.getcolumnidx("groupID")
        idx_groupname = group_table.getcolumnidx("groupName")
        for datarow in group_table.datarows:
            name = datarow[idx_groupname]
            if not name in group_name_id:
                group_name_id[name] = datarow[idx_groupid]
            else:
                group_name_collisions.add(name)
            name_stripped = re.sub("\s", "", name)
            if not name_stripped in group_name_id:
                group_name_id[name_stripped] = datarow[idx_groupid]
            else:
                group_name_collisions.add(name_stripped)
        # And for types
        type_name_id = {}
        type_name_collisions = set()
        type_table = self.tables["invtypes"]
        idx_typeid = type_table.getcolumnidx("typeID")
        idx_typename = type_table.getcolumnidx("typeName")
        for datarow in type_table.datarows:
            name = datarow[idx_typename]
            if not name in type_name_id:
                type_name_id[name] = datarow[idx_typeid]
            else:
                type_name_collisions.add(name)
            name_stripped = re.sub("\s", "", name)
            if not name_stripped in type_name_id:
                type_name_id[name_stripped] = datarow[idx_typeid]
            else:
                type_name_collisions.add(name_stripped)
        # Get column indices for all required columns in expression table
        exp_table = self.tables["dgmexpressions"]
        idx_operand = exp_table.getcolumnidx("operandID")
        idx_expvalue = exp_table.getcolumnidx("expressionValue")
        idx_expattr = exp_table.getcolumnidx("expressionAttributeID")
        idx_expgroup = exp_table.getcolumnidx("expressionGroupID")
        idx_exptype = exp_table.getcolumnidx("expressionTypeID")
        # Create replacement map which will store old and new data rows
        # Format: {current data row: replacement data row}
        replacement_map = {}
        # Values which are considered to be empty
        nulls = {None, 0}
        for datarow in exp_table.datarows:
            operand = datarow[idx_operand]
            # Process attributes
            if operand == const.operand_DEFATTR:
                attr = datarow[idx_expattr]
                val = datarow[idx_expvalue]
                if attr in nulls and val in attr_name_id:
                    if val in attr_name_collisions:
                        print("  Warning: use of colliding attribute name {0} detected, expect errors".format(val))
                    mutablerow = list(datarow)
                    mutablerow[idx_expattr] = attr_name_id[val]
                    mutablerow[idx_expvalue] = None
                    replacementrow = tuple(mutablerow)
                    replacement_map[datarow] = replacementrow
            # Groups
            elif operand == const.operand_DEFGRP:
                group = datarow[idx_expgroup]
                val = datarow[idx_expvalue]
                if group in nulls and val in group_name_id:
                    if val in group_name_collisions:
                        print("  Warning: use of colliding group name {0} detected, expect errors".format(val))
                    mutablerow = list(datarow)
                    mutablerow[idx_expgroup] = group_name_id[val]
                    mutablerow[idx_expvalue] = None
                    replacementrow = tuple(mutablerow)
                    replacement_map[datarow] = replacementrow
            # And types
            elif operand == const.operand_DEFTYPE:
                invtype = datarow[idx_exptype]
                val = datarow[idx_expvalue]
                if invtype in nulls and val in type_name_id:
                    if val in type_name_collisions:
                        print("  Warning: use of colliding type name {0} detected, expect errors".format(val))
                    mutablerow = list(datarow)
                    mutablerow[idx_exptype] = type_name_id[val]
                    mutablerow[idx_expvalue] = None
                    replacementrow = tuple(mutablerow)
                    replacement_map[datarow] = replacementrow
        # Do actual replacements
        for datarow in replacement_map:
            exp_table.datarows.remove(datarow)
            exp_table.datarows.add(replacement_map[datarow])
        return

    def __manual_filter_invtypes(self):
        """Filter undesired data rows from invtypes table"""
        # Set with categoryIDs we want to keep
        valid_categories = {const.category_SHIP, const.category_MODULE, const.category_CHARGE,
                            const.category_SKILL, const.category_DRONE, const.category_IMPLANT,
                            const.category_SUBSYSTEM}
        # Set with groupIDs we want to keep
        valid_groups = {const.group_EFFECTBEACON}
        # Get ndices of group and category columns in group table
        group_table = self.tables["invgroups"]
        idx_groupid = group_table.getcolumnidx("groupID")
        idx_categoryid = group_table.getcolumnidx("categoryID")
        # Go through table data, filling valid groups set according to valid categories
        for datarow in group_table.datarows:
            if datarow[idx_categoryid] in valid_categories:
                valid_groups.add(datarow[idx_groupid])
        # Find out rows not in valid groups and mark them as to be removed
        type_table = self.tables["invtypes"]
        idx_groupid = type_table.getcolumnidx("groupID")
        toremove = set()
        for datarow in type_table.datarows:
            if not datarow[idx_groupid] in valid_groups:
                toremove.add(datarow)
        # Move data to our 'trash bin'
        type_removed = self.removed_data["invtypes"]
        for datarow in toremove:
            if not datarow in type_removed:
                type_removed[datarow] = const.removal_FILTER
            type_table.datarows.remove(datarow)
        return

    def __process_manual_strongs(self):
        """Add manually specified strong data to internal temporary storage"""
        # Go through all tables in specifications
        for tabname in self.dbspec:
            table = self.tables[tabname]
            # All their columns
            for colname in self.dbspec[tabname].columns:
                # Check strong values section
                strong_vals = self.dbspec[tabname].columns[colname].strongvals
                # If it's empty, go on
                if strong_vals is None:
                    continue
                # Create sub-dictionary for table if it doesn't have it yet
                if not tabname in self.strong_data:
                    self.strong_data[tabname] = {}
                # Get index of column in question
                colidx = table.getcolumnidx(colname)
                # If it's not yet in sub-dictionary, add it as key and corresponding
                # set as value
                if not colidx in self.strong_data[tabname]:
                    self.strong_data[tabname][colidx] = set()
                # Add values to set
                self.strong_data[tabname][colidx].update(strong_vals)
        return

    def __cyclic_autocleanup(self):
        """Automatically removed data with broken links or no links to it from database"""
        # Define local auxiliary dictionaries for FK relations
        # 1:1 source-target relation
        # {source table: {source column: target}}
        src_fk_tgt = {}
        # 1:many target-source relation
        # {target table: {target column: sources}}
        tgt_fk_src = {}
        # Go through all tables to fill maps with proper containers for actual data
        for tabname in self.tables:
            table = self.tables[tabname]
            for column in table.columns:
                if column.fk is None:
                    continue
                fktabname, fkcolname = column.fk.split(".")
                fktable = self.tables[fktabname]
                fkcolumn = fktable.getcolumn(fkcolname)
                # Fill source-target map
                if not table.name in src_fk_tgt:
                    src_fk_tgt[table.name] = {}
                src_fk_tgt[table.name][column.name] = "{0}.{1}".format(fktable.name, fkcolumn.name)
                # And target-source
                if not fktable.name in tgt_fk_src:
                    tgt_fk_src[fktable.name] = {}
                if not fkcolumn.name in tgt_fk_src[fktable.name]:
                    tgt_fk_src[fktable.name][fkcolumn.name] = set()
                tgt_fk_src[fktable.name][fkcolumn.name].add("{0}.{1}".format(table.name, column.name))

        # Changes flag, set to True for first cycle
        changed = True
        # We will cycle if we had any changes on previous cycle, we need to run
        # additional cycles, because new broken rows may appear after removal of
        # other rows previous cycle
        while changed is True:
            # Re-set changes flag
            changed = False
            # Container for column data, we need to have it to re-use gathered data,
            # but we need to refresh it each cycle
            # { table.column : set(data) }
            coldata = {}
            # Fill it with data, first for columns which are FKs
            for tabname in src_fk_tgt:
                for colname in src_fk_tgt[tabname]:
                    key = "{0}.{1}".format(tabname, colname)
                    if not key in coldata:
                        coldata[key] = self.tables[tabname].getcolumndataset(colname)
            # Then with data for columns which are referenced by other columns
            for tabname in tgt_fk_src:
                for colname in tgt_fk_src[tabname]:
                    key = "{0}.{1}".format(tabname, colname)
                    if not key in coldata:
                        coldata[key] = self.tables[tabname].getcolumndataset(colname)
            # Go through data container and remove zero from every set, as
            # CCP seem to set zeros in some cases when they should've set None
            for column in coldata:
                coldata[column].difference_update({0})
            # Do actual cleaning
            for tabname in self.tables:
                table = self.tables[tabname]
                # First, rows with broken FK references to other columns
                if tabname in src_fk_tgt:
                    for fkcolname in src_fk_tgt[tabname]:
                        src = "{0}.{1}".format(tabname, fkcolname)
                        tgt = src_fk_tgt[tabname][fkcolname]
                        # Get set of values which represent broken references
                        brokenvals = coldata[src].difference(coldata[tgt])
                        # Get column index for proper data processing
                        colidx = table.getcolumnidx(fkcolname)
                        # Fill set with rows we'll have to remove
                        toremove = set()
                        for datarow in table.datarows:
                            # Add those rows with column value corresponding to broken one
                            if datarow[colidx] in brokenvals:
                                toremove.add(datarow)
                        # Now, get number of rows we'll need to remove
                        rmcount = len(toremove)
                        # And do anything only when we have something there
                        if rmcount > 0:
                            # Actually remove rows
                            removed_data = self.removed_data[table.name]
                            for datarow in toremove:
                                if not datarow in removed_data:
                                    removed_data[datarow] = const.removal_BROKEN_REF
                            table.datarows.difference_update(toremove)
                            # Set changes flag to run one more iteration
                            changed  = True
                # Get strength status of table
                tabstrength = self.dbspec[tabname][1]
                # We don't want to process "strong" tables - tables, for which we don't
                # want to delete data rows even if there're no references to it
                if tabname in tgt_fk_src and tabstrength is not True:
                    # Get strong data info for current table
                    strongrows = self.strong_data.get(tabname)
                    for colname in tgt_fk_src[tabname]:
                        # Workflow is almost the same with small exceptions
                        tgt = "{0}.{1}".format(tabname, colname)
                        # Get reference values for all FKs referencing to this column
                        references = set()
                        for src in tgt_fk_src[tabname][colname]:
                            references.update(coldata[src])
                        # Find which values of given column are not referenced
                        norefs = coldata[tgt].difference(references)
                        colidx = table.getcolumnidx(colname)
                        # Compose set of rows we'll need to remove due to lack of reference
                        toremove = set()
                        # Follow simple way if we do not have any strong data
                        if strongrows is None:
                            for datarow in table.datarows:
                                if datarow[colidx] in norefs:
                                    toremove.add(datarow)
                        # If we have some, take them into consideration
                        else:
                            for datarow in table.datarows:
                                if datarow[colidx] in norefs:
                                    # Assume that we're going to remove this row by default
                                    rm = True
                                    # Make an additional check for strong data
                                    for strongcolidx in strongrows:
                                        if datarow[strongcolidx] in strongrows[strongcolidx]:
                                            # When we find first match, mark row as not being removed
                                            # and break the exceptions loop
                                            rm = False
                                            break
                                    # Add row to removed set only if it's not suitable for any of our
                                    # exceptions
                                    if rm is True:
                                        toremove.add(datarow)
                        rmcount = len(toremove)
                        # Run actual removal if set is not empty
                        if rmcount > 0:
                            removed_data = self.removed_data[table.name]
                            for datarow in toremove:
                                if not datarow in removed_data:
                                    removed_data[datarow] = const.removal_NO_REF_TO
                            table.datarows.difference_update(toremove)
                            changed  = True
        return

    def __restore_surface_attrrefereces(self):
        """
        Restores target items for attributes targeting types, groups and other attributes. This is
        useful in cases if some entity is referenced by attribute, and we want to show some basic info
        about it (e.g. show "Strontium Clatrates" as consumption type instead of just ID, when looking at
        siege module attributes). Please note that this method takes only such 'surface' references, it
        doesn't pick up any related data of restored references (e.g. mentioned siege ammo will come
        without any attributes or effects).
        """
        # Some high-level access instructions, what to restore
        restore_datas = {(const.attributeCategory_DEFATTR, "dgmattribs", "attributeID"),
                         (const.attributeCategory_DEFGROUP, "invgroups", "groupID"),
                         (const.attributeCategory_DEFTYPE, "invtypes", "typeID")}
        # Go through each of them
        for restore_data in restore_datas:
            # Container for attribute IDs which reference corresponding entity
            attrs_entity = set()
            # Get table and appropriate columns' indices
            attr_table = self.tables["dgmattribs"]
            idx_attrid = attr_table.getcolumnidx("attributeID")
            idx_attrcat = attr_table.getcolumnidx("attributeCategory")
            # Fill sets with actual attribute IDs which are used to reference that entity
            for datarow in attr_table.datarows:
                attrcat = datarow[idx_attrcat]
                if attrcat == restore_data[0]:
                    attrs_entity.add(datarow[idx_attrid])
            # Get indices to work with data in dgmtypeattribs table
            typeattrs_table = self.tables["dgmtypeattribs"]
            idx_attrid = typeattrs_table.getcolumnidx("attributeID")
            idx_value = typeattrs_table.getcolumnidx("value")
            # Container for IDs of entities we're going to restore
            restore_entities = set()
            # Cycle through data rows and see if we get attribute ID match
            for datarow in typeattrs_table.datarows:
                # If we do, write down ID of entity to corresponding set
                if datarow[idx_attrid] in attrs_entity:
                    value = datarow[idx_value]
                    if not value in {0, None}:
                        restore_entities.add(int(value))
            # Restore entities
            entity_tablename = restore_data[1]
            entity_idcolname = restore_data[2]
            torestore = set()
            idx_entityid = self.tables[entity_tablename].getcolumnidx(entity_idcolname)
            for datarow in self.removed_data[entity_tablename]:
                if datarow[idx_entityid] in restore_entities:
                    torestore.add(datarow)
            self.tables[entity_tablename].datarows.update(torestore)
            for datarow in torestore:
                del self.removed_data[entity_tablename][datarow]
        return

    def __print_stats(self):
        """Print statistics about removed data"""
        # Print some statistics
        for tabname in sorted(self.removed_data):
            removed_data = self.removed_data[tabname]
            # Get number of items removed due to some reason
            filtered = 0
            noref = 0
            brokenref = 0
            for datarow in removed_data:
                reason = removed_data[datarow]
                if reason == const.removal_FILTER:
                    filtered += 1
                elif reason == const.removal_NO_REF_TO:
                    noref += 1
                elif reason == const.removal_BROKEN_REF:
                    brokenref += 1
            # Print anything only if we've done something with table
            if brokenref > 0 or noref > 0 or filtered > 0:
                # Calculate total number of data rows we had in table
                startrowlen = len(self.tables[tabname].datarows) + len(removed_data)
                # Container for text data
                rmtypes = []
                # Also don't print data for removal types which didn't
                # affect given table
                if filtered > 0:
                    plu = "" if filtered == 1 else "s"
                    perc = 100.0 * filtered / startrowlen
                    rmtypes.append("{0} row{1} ({2:.1f}%) removed (removed by data filter)".format(filtered, plu, perc))
                if brokenref > 0:
                    plu = "" if brokenref == 1 else "s"
                    perc = 100.0 * brokenref / startrowlen
                    rmtypes.append("{0} row{1} ({2:.1f}%) removed (broken references)".format(brokenref, plu, perc))
                if noref > 0:
                    plu = "" if noref == 1 else "s"
                    perc = 100.0 * noref / startrowlen
                    rmtypes.append("{0} row{1} ({2:.1f}%) removed (no incoming references)".format(noref, plu, perc))
                # Actual line print
                print("  Table {0} cleaned: {1}".format(tabname, ", ".join(rmtypes)))
        return
