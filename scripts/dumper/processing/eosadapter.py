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
        print("Refactoring database for Eos")
        self.dbspec = self.__get_dbspec()
        # Delete malformed entries in both structures; also, fill actual data
        # with additional flags taken from custom data specification
        self.__synch_dbinfo()
        # Old workflow is still kept here
        self.filterspec = self.__get_filterspec()
        self.exceptspec = self.__get_exceptspec()
        self.__database_refactor()

    def __get_dbspec(self):
        """Return specification of data Eos needs"""
        # Data specification, container for tables:
        # { table name : [ columns, strength ] }
        # Table specification, container for columns
        # { column name : [ foreign.key, index, noref exceptions ] }
        dataspec = {}

        dataspec["dgmattribs"] = TableSpec({}, False)
        dgmattribs = dataspec["dgmattribs"].columns
        dgmattribs["attributeID"] = ColumnSpec(None, False, None)
        dgmattribs["attributeName"] = ColumnSpec(None, False, {"radius", "mass", "volume", "capacity"})
        #dgmattribs["attributeCategory"] = ColumnSpec(None, False, None)
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

    def __get_filterspec(self):
        # Data filter specification
        # ( table to clean, with column used as key, join statements, filter )
        filterspec = (("invtypes.typeID", "invtypes.groupID = invgroups.groupID | invgroups.categoryID = invcategories.categoryID", "invcategories.categoryName(Ship, Module, Charge, Skill, Drone, Implant, Subsystem) | invgroups.groupName(Effect Beacon)"),)
        return filterspec

    def __get_exceptspec(self):
        # Additional exception specification, values from here won't be removed when there're no direct references to them
        # ( reference to keys of table for which we're making exception = values of the key to keep, additional condition, join statements )
        exceptspec = (("dgmattribs.attributeID = dgmtypeattribs.value", "eveunits.displayName = attributeID", "invtypes.typeID = dgmtypeattribs.typeID | dgmtypeattribs.attributeID = dgmattribs.attributeID | dgmattribs.unitID = eveunits.unitID"),
                      ("invgroups.groupID = dgmtypeattribs.value", "eveunits.displayName = groupID", "invtypes.typeID = dgmtypeattribs.typeID | dgmtypeattribs.attributeID = dgmattribs.attributeID | dgmattribs.unitID = eveunits.unitID"),
                      ("invtypes.typeID = dgmtypeattribs.value", "eveunits.displayName = typeID", "invtypes.typeID = dgmtypeattribs.typeID | dgmtypeattribs.attributeID = dgmattribs.attributeID | dgmattribs.unitID = eveunits.unitID"))
        return exceptspec

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
                if column.datatype != const.INT:
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

    def __database_refactor(self):
        """
        Refactor database according to passed specification
        """
        # Gather number of data rows for statistics
        rowlen = {}
        for tabname in self.tables:
            rowlen[tabname] = len(self.tables[tabname].datarows)

        # Dictionaries to track number of removed rows per table
        rmvd_filter = {}
        rmvd_brokenref = {}
        rmvd_norefto = {}
        # Fill them with zeros for all tables by default
        for tabname in self.tables:
            rmvd_filter[tabname] = 0
            rmvd_brokenref[tabname] = 0
            rmvd_norefto[tabname] = 0

        ## STAGE 2: remove data according to provided specification
        # Storage for data which was filtered out
        # { table : set(data rows) }
        filteredout = {}

        # Run table data filters
        for rowfilter in self.filterspec:
            success = self.__table_filter(self.tables, rowfilter, rmvd_filter, filteredout)
            # Print some notification if we had errors during its processing
            if success is False:
                print("  Data filtering failed, please revise filter specification")

        ## STAGE 3: exception processing: sometimes we have to leave some
        ## data in the database (protect it from automatic removal), exceptions
        ## serve solely this purpose. There're 2 types of exceptions: hard-coded by column
        ## value in general database specifications and flexible filter-based exceptions
        # Custom local data structure for exception stuff
        # { table name : {column index : set (exception values) } }
        exceptions = {}
        # Fill hard-coded exceptions
        # Go through all tables in specifications
        for tabname in self.dbspec:
            table = self.tables[tabname]
            # All their columns
            for colname in self.dbspec[tabname][0]:
                # Check exceptions section
                excspec = self.dbspec[tabname][0][colname][2]
                # If it's empty, go on
                if excspec is None:
                    continue
                # Create sub-dictionary for table if it doesn't have it yet
                if not tabname in exceptions:
                    exceptions[tabname] = {}
                # Get index of column in question
                colidx = table.columns.index(table.getcolumn(colname))
                # If it's not yet in sub-dictionary, add it as key and corresponding
                # set as value
                if not colidx in exceptions[tabname]:
                    exceptions[tabname][colidx] = set()
                # Add values to set
                exceptions[tabname][colidx].update(set(excspec))

        # Now, process flexible filter-based exception definitions
        # Exception error flag
        excerrors = False
        # Changes flag, True for first iteration
        changed = True
        # Set with erroneous specifications, used to skip corrupted
        # ones on 2nd iteration and further
        errexcspecs = set()
        # Cycle as long as previous cycle changed the database
        # We need multiple cycles to make sure re-added data gets its
        # references back into database too
        while(changed):
            # Re-set changes flag
            changed = False
            # Cycle through entries in exception definitions
            for exc in self.exceptspec:
                # Check if this specification is know to be erroneous
                if exc in errexcspecs:
                    # And skip if it is
                    continue
                # Run series of checks on each before doing anything,
                # If we found anything bad just skip definition
                if len(exc) != 3:
                    print("  Exception specification malformed")
                    excerrors = True
                    errexcspecs.add(exc)
                    continue
                eqcond = exc[0]
                valcond = exc[1]
                joinspec = exc[2]
                eqcondsplit = eqcond.split("=")
                if len(eqcondsplit) != 2:
                    print("  Exception equality condition malformed")
                    excerrors = True
                    errexcspecs.add(exc)
                    continue
                valcondsplit = valcond.split("=")
                if len(valcondsplit) != 2:
                    print("  Exception value condition malformed")
                    excerrors = True
                    errexcspecs.add(exc)
                    continue
                # Auxiliary data set, stores potential table.column references from
                # first two fields of exception specification
                tabcols = set()
                exctarget = eqcondsplit[0].strip()
                tabcols.add(exctarget)
                excsource = eqcondsplit[1].strip()
                tabcols.add(excsource)
                filtertabcol = valcondsplit[0].strip()
                tabcols.add(filtertabcol)
                filtervalue = valcondsplit[1].strip()
                # Check references in auxiliary data set
                for tabcol in tabcols:
                    tabcolsplit = tabcol.split(".")
                    if len(tabcolsplit) != 2:
                        print("  Table reference in exception definition malformed: {0}".format(tabcol))
                        errexcspecs.add(exc)
                        break
                    tabname = tabcolsplit[0]
                    colname = tabcolsplit[1]
                    if not tabname in self.tables:
                        print("  Unable to find table specified in exception definition: {0}".format(tabname))
                        errexcspecs.add(exc)
                        break
                    if self.tables[tabname].getcolumn(colname) is None:
                        print("  Unable to find column of table {0} specified in exception definition: {1}".format(tabname, colname))
                        errexcspecs.add(exc)
                        break
                if exc in errexcspecs:
                    excerrors = True
                    continue
                # Start doing actual job; join columns as stated in join statement set
                success, joinedcols, joinedrows = self.__table_join(self.tables, joinspec)
                # Bail in case of any errors, as usual
                if success is not True:
                    excerrors = True
                    errexcspecs.add(exc)
                    continue
                # Get index of the column by which we're going to filer
                excfiltabname = filtertabcol.split(".")[0]
                excfilcolname = filtertabcol.split(".")[1]
                try:
                    excfilidx = joinedcols.index(self.tables[excfiltabname].getcolumn(excfilcolname))
                # Error for case when such column wasn't found in joined table
                except ValueError:
                    print("  Unable to find exception filter column {0} in joined table".format(filtertabcol))
                    excerrors = True
                    errexcspecs.add(exc)
                    continue
                # The same, but for column from which we'll take value
                excsrctabname = excsource.split(".")[0]
                excsrccolname = excsource.split(".")[1]
                try:
                    excsrcidx = joinedcols.index(self.tables[excsrctabname].getcolumn(excsrccolname))
                # Error for case when such column wasn't found in joined table
                except ValueError:
                    print("  Unable to find exception source data column {0} in joined table".format(excsource))
                    excerrors = True
                    errexcspecs.add(exc)
                    continue
                # Data storage for values which we'll add to exception dictionary
                toexcept = set()
                for row in joinedrows:
                    # Compare each row value for specified column against
                    # value mentioned in specification
                    if row[excfilidx] == filtervalue:
                        val = row[excsrcidx]
                        if val is not None:
                            toexcept.add(val)
                # Finally, update exceptions list; get exception target column
                # coordinates in textual form
                exctgttabname = exctarget.split(".")[0]
                exctgtcolname = exctarget.split(".")[1]
                # If nothing was there, un-nothing it
                if not exctgttabname in exceptions:
                    exceptions[exctgttabname] = {}
                # Get index of target column in target table
                exctgtcolidx = self.tables[exctgttabname].columns.index(self.tables[exctgttabname].getcolumn(exctgtcolname))
                # Un-nothing column data set for target table too
                if not exctgtcolidx in exceptions[exctgttabname]:
                    exceptions[exctgttabname][exctgtcolidx] = set()
                # And add our new values
                exceptions[exctgttabname][exctgtcolidx].update(toexcept)

            # Here we'll restore data, as specified in exceptions data structure,
            # we need to do it each cycle
            # Check all tables which were filtered by manually
            # specified filter
            for tabname in filteredout:
                # If given table has no exceptions defined, it's okay, just skip it
                if not tabname in exceptions:
                    continue
                # Set-container for rows which we'll put back to table
                putback = set()
                # Go through all exception columns for given table
                for colidx in exceptions[tabname]:
                    # Find list of data to be excepted
                    excepted = exceptions[tabname][colidx]
                    # If we filtered any data which is excepted, add it to set
                    for datarow in filteredout[tabname]:
                        if datarow[colidx] in excepted:
                            putback.add(datarow)
                # Do anything only if we have something we actually should restore
                if len(putback) > 0:
                    # Actually return data to dictionary
                    self.tables[tabname].datarows.update(putback)
                    # And remove it from filtered out columns
                    filteredout[tabname].difference_update(putback)
                    # Also modify statistics counter to properly reflect it
                    rmvd_filter[tabname] -= len(putback)
                    # Set changes flag back
                    changed = True

        # Final message for this block, if we had any errors
        if excerrors is True:
            print("  Please revise exceptions specification")

        ## STAGE 4: automatic removal of data with no references to it or
        ## broken references
        # Define local auxiliary dictionaries for FK relations
        # 1:1 source-target relation
        # { source table : { source column : target } }
        src_fk_tgt = {}
        # 1:many target-source relation
        # { target table : { target column : sources } }
        tgt_fk_src = {}

        for tabname in self.tables:
            table = self.tables[tabname]
            for column in table.columns:
                if column.fk is None:
                    continue
                fktabname, fkcolname = column.fk.split(".")
                fktable = self.tables[fktabname]
                fkcolumn = fktable.getcolumn(fkcolname)
                # Also store in local structures; source-target map
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
                        colidx = table.columns.index(table.getcolumn(fkcolname))
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
                            table.datarows.difference_update(toremove)
                            # Update count of removed rows due to broken references
                            rmvd_brokenref[table.name] += rmcount
                            # Set changes flag to run one more iteration
                            changed  = True
                # Get strength status of table
                tabstrength = self.dbspec[tabname][1]
                # We don't want to process "strong" tables - tables, for which we don't
                # want to delete data rows even if there're no references to it
                if tabname in tgt_fk_src and tabstrength is not True:
                    # Get no reference exceptions for current table
                    norefexc = exceptions.get(tabname)
                    for colname in tgt_fk_src[tabname]:
                        # Workflow is almost the same with small exceptions
                        tgt = "{0}.{1}".format(tabname, colname)
                        # Get reference values for all FKs referencing to this column
                        references = set()
                        for src in tgt_fk_src[tabname][colname]:
                            references.update(coldata[src])
                        # Find which values of given column are not referenced
                        norefs = coldata[tgt].difference(references)
                        colidx = table.columns.index(table.getcolumn(colname))
                        # Compose set of rows we'll need to remove due to lack of reference
                        toremove = set()
                        # Follow simple way if we do not have any exceptions
                        if norefexc is None:
                            for datarow in table.datarows:
                                if datarow[colidx] in norefs:
                                    toremove.add(datarow)
                        # If we have some, take them into consideration
                        else:
                            for datarow in table.datarows:
                                if datarow[colidx] in norefs:
                                    # Assume that we're going to remove this row by default
                                    rm = True
                                    # Make an additional check for exceptions
                                    for exccolidx in norefexc:
                                        if datarow[exccolidx] in norefexc[exccolidx]:
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
                            table.datarows.difference_update(toremove)
                            # Fill another dictionary for entries removed due to
                            # absence of references
                            rmvd_norefto[table.name] += rmcount
                            changed  = True

        # Print some statistics
        for tabname in sorted(self.tables.iterkeys()):
            # Get number of items removed due to some reason
            filtered = rmvd_filter[tabname]
            brokenref = rmvd_brokenref[tabname]
            noref = rmvd_norefto[tabname]
            # Print anything only if we've done something with table
            if brokenref > 0 or noref > 0 or filtered > 0:
                rmtypes = []
                # Also don't print data for removal types which didn't
                # affect given table
                if filtered > 0:
                    plu = "" if filtered == 1 else "s"
                    perc = 100.0 * filtered / rowlen[tabname]
                    rmtypes.append("{0} row{1} ({2:.1f}%) removed (removed by data filter)".format(filtered, plu, perc))
                if brokenref > 0:
                    plu = "" if brokenref == 1 else "s"
                    perc = 100.0 * brokenref / rowlen[tabname]
                    rmtypes.append("{0} row{1} ({2:.1f}%) removed (broken references)".format(brokenref, plu, perc))
                if noref > 0:
                    plu = "" if noref == 1 else "s"
                    perc = 100.0 * noref / rowlen[tabname]
                    rmtypes.append("{0} row{1} ({2:.1f}%) removed (no incoming references)".format(noref, plu, perc))
                # Actual line print
                print("  Table {0} cleaned: {1}".format(tabname, ", ".join(rmtypes)))
        return

    def __table_filter(self, tables, rmspec, statsdict, filteredout):
        """
        Filters one of the tables according to provided specification
        """
        # Error flag, indicating any errors occurred during removal specification
        if len(rmspec) != 3:
            print("  Malformed data filter specification")
            return False
        # Divide removal specification into several parts
        # Also clean up space characters in the places where they're not
        # significant for our convenience
        rmentity = re.sub("[\s]+", "", rmspec[0])
        joinspec = rmspec[1]
        filterspec = rmspec[2]

        # Join tables
        success, joinedcols, joinedrows = self.__table_join(tables, joinspec)
        # If we had some errors during join, just bail
        if success is not True:
            return False

        # Now, when we have our joined table ready, start filtering jobs
        # Use this data structure to hold filter data
        # { filter column index : set(acceptable filter values) }
        filters = {}
        # Go through all filters separated by OR sign
        for rowfilter in filterspec.split("|"):
            # Use regexp for matching
            match = re.search("([\w]+\.[\w]+)\(([\w ]+(,[\w ]+)*)\)", rowfilter)
            # If we have some  entry with no regexp match, something must've gone wrong
            if match is None:
                print("  Malformed filter statement")
                return False
            # Get full coordinates of filter column
            fullname = match.group(1)
            # Split them into table and column names
            fullnamesplit = fullname.split(".")
            # Check length
            if len(fullnamesplit) != 2:
                print("  Malformed filter specification")
                return False
            tabname, colname = fullnamesplit
            # Check if referred table and column exist
            if not tabname in tables:
                print("  Filter specification refers to non-existing table")
                return False
            if tables[tabname].getcolumn(colname) is None:
                print("  Filter specification refers to non-existing column")
                return False
            # Get position of column by which we're going to perform filtering
            filtercolidx = joinedcols.index(tables[tabname].getcolumn(colname))
            # Then, get acceptable values for given filter
            filternames = match.group(2)
            # If there's no such position index in filter data structure, create
            # empty set under position key
            if not filtercolidx in filters:
                filters[filtercolidx] = set()
            # Fill this set with acceptable filter values
            for filtername in filternames.split(","):
                filters[filtercolidx].add(filtername.strip())
        # Get table and column names which will be used to address filtered values
        rmentsplit = rmentity.split(".")
        # Check for table.column format
        if len(rmentsplit) != 2:
            print("  Malformed removal primary key specification")
            return False
        filtable, filcolumn = rmentsplit
        # Check if these tables and columns actually exist
        if not filtable in tables:
            print("  Removal primary key specification refers to non-existing table")
            return False
        if tables[filtable].getcolumn(filcolumn) is None:
            print("  Removal primary key specification refers to non-existing column")
            return False
        # Get position of this column in custom column structure
        filtercolidx = joinedcols.index(tables[filtable].getcolumn(filcolumn))
        # This set will hold values to keep; rows with such values in filter column
        # won't be deleted
        tokeep = set()
        # Go through all rows of joined table
        for row in joinedrows:
            # Check for match against any filter
            for rowfilter in filters:
                # If we find match, note down to keep this row and break
                # iteration over filters
                if row[rowfilter] in filters[rowfilter]:
                    tokeep.add(row[filtercolidx])
                    break
        # This set will contain rows to remove
        toremove = set()
        # Get position of the same filter column, but this time in original table
        origidx = tables[filtable].columns.index(tables[filtable].getcolumn(filcolumn))
        # Cycle through data rows of that original table
        for row in tables[filtable].datarows:
            # If we didn't decide to keep row with such key column value
            if row[origidx] not in tokeep:
                # Mark it for removal
                toremove.add(row)
        # Actually remove rows from table
        tables[filtable].datarows.difference_update(toremove)
        # Update dictionary tracking removed columns
        if filtable not in filteredout:
            filteredout[filtable] = set()
        filteredout[filtable].update(toremove)
        # Add number of rows removed to per-filter removed data counter
        statsdict[filtable] += len(toremove)
        # If we got here, it's success
        return True

    def __table_join(self, tables, joinspec):
        """
        Join tables according to provided specification
        """
        # Auxiliary dictionary, which contains data from several tables keyed
        # by the column we need
        # { table name : { key name : set(data rows) } }
        keyed = {}
        # Fill small auxiliary set with table.columns we want to have keyed
        keycolumns = set()
        # Strip white spaces from specification
        joinspec = re.sub("[\s]+", "", joinspec)
        # Go through all join equations
        for jn in joinspec.split("|"):
            parts = jn.split("=")
            # Check if there're actually 2 parts
            if len(parts) != 2:
                print("  Malformed join statement")
                return False, [], set()
            for part in parts:
                # Then, check if each part is full reference
                reference = part.split(".")
                if len(reference) != 2:
                    print("  Malformed part of join statement")
                    return False, [], set()
                # Also check if such tables actually exist
                tabname, colname = reference
                if not tabname in tables:
                    print("  Join statement refers to non-existing table")
                    return False, [], set()
                if tables[tabname].getcolumn(colname) is None:
                    print("  Join statement refers to non-existing column")
                    return False, [], set()
            # We assume that left part of join is already joined, so we'll need
            # just key on its right part
            keycolumns.add(parts[1])
        # Create sub-containers in keyed tables dictionary
        for keycolumn in keycolumns:
            tabname, colname = keycolumn.split(".")
            if not tabname in keyed:
                keyed[tabname] = {}
            if not colname in keyed[tabname]:
                keyed[tabname][colname] = {}
        # And fill them with data from our tables
        for tabname in keyed:
            table = tables[tabname]
            for keycolname in keyed[tabname]:
                # Just make reference to our keyed data container
                keyedata = keyed[tabname][keycolname]
                # Find index of key column in column sequence of the table
                keyidx = table.columns.index(table.getcolumn(keycolname))
                # Go through all data rows of original table
                for datarow in table.datarows:
                    keyval = datarow[keyidx]
                    # Ignore rows with None value, as we won't join on them anyway
                    if keyval is None:
                        continue
                    # Create set with data for each new key
                    if not keyval in keyedata:
                        keyedata[keyval] = set()
                    # Finally, add actual data row to it
                    keyedata[keyval].add(datarow)
        # Container for columns of joined table
        joinedcols = []
        # Container for joined rows, initialized to None
        joinedrows = None
        # Auxiliary data set, to avoid joining on the same table twice
        joinedtabs = set()
        # Go through all join equations once again
        for jn in joinspec.split("|"):
            # Separate them in left and right part
            left, right = jn.split("=")
            # Separate both into table name and column name
            ltabname, lcolname = left.split(".")
            rtabname, rcolname = right.split(".")
            # Check if left part is already included into our data structure
            if not ltabname in joinedtabs:
                # It's allowed to be not included only for leftmost join
                if joinedrows is None:
                    # Re-initialize data container
                    joinedrows = set()
                    # Fill it with data of left table
                    joinedrows.update(tables[ltabname].datarows)
                    # Do the same for columns and auxiliary table name store
                    joinedcols += list(tables[ltabname].columns)
                    joinedtabs.add(ltabname)
                # Error time, left part always must be joined
                else:
                    print("  All left parts of join statements (except for the leftmost one) must be joined")
                    return False, [], set()
            # Check if we didn't join left part already
            if not rtabname in joinedtabs:
                # Temporary structure to hold data for current join
                tmprows = set()
                # Get position of left column in current custom column structure
                ljoincolidx = joinedcols.index(tables[ltabname].getcolumn(lcolname))
                # Cycle through data rows of left table
                for row in joinedrows:
                    # Get left join value
                    joinval = row[ljoincolidx]
                    # Do anything only if it's not None and there's key with such value
                    # in right table
                    if joinval is not None and joinval in keyed[rtabname][rcolname]:
                        # Get rows which have right join value equal to left join value
                        rightrows = keyed[rtabname][rcolname][joinval]
                        # Cycle through them
                        for rightrow in rightrows:
                            # Compose new row by dumb data concatenating
                            newrow = tuple(list(row) + list(rightrow))
                            # Add new row to temporary set
                            tmprows.add(newrow)
                # When we're done, mark right table as joined
                joinedtabs.add(rtabname)
                # Concatenate columns too
                joinedcols += list(tables[rtabname].columns)
                # And re-assign temporary set to main joined data set
                joinedrows = tmprows
            # Right table always must be non-joined
            else:
                print("  All right parts of join statements must be not joined")
                return False, [], set()
        return True, joinedcols, joinedrows

