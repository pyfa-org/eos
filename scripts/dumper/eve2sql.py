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

"""
This script pulls data out of EVE cache and makes an SQLite dump
Reverence library by Entity is used, check http://wiki.github.com/ntt/reverence/ for source code
Example commands to run the script for default paths under Linux to get SQLite dump:
Tranquility: python eve2sql.py --eve="~/.wine/drive_c/Program Files/CCP/EVE" --cache="~/.wine/drive_c/users/"$USER"/Local Settings/Application Data/CCP/EVE/c_program_files_ccp_eve_tranquility/cache" --sqlite="/home/"$USER"/Desktop/eve.db"
Singularity: python eve2sql.py --eve="~/.wine/drive_c/Program Files/CCP/Singularity" --cache="~/.wine/drive_c/users/"$USER"/Local Settings/Application Data/CCP/EVE/c_program_files_ccp_singularity_singularity/cache" --sisi --sqlite="/home/"$USER"/Desktop/evetest.db"
"""

def get_eosdataspec():
    """
    Return specification of data Eos needs
    """
    # Data specification, container for tables:
    # { table name : [ columns, strength ] }
    # Table specification, container for columns
    # { column name : [ foreign.key, index, noref exceptions ] }
    dataspec = {}

    dataspec["dgmattribs"] = [{}, False]
    dgmattribs = dataspec["dgmattribs"][0]
    dgmattribs["attributeID"] = [None, False, None]
    dgmattribs["attributeName"] = [None, False, {"radius", "mass", "volume", "capacity"}]
    #dgmattribs["attributeCategory"] = [None, False, None]
    #dgmattribs["description"] = [None, False, None]
    dgmattribs["maxAttributeID"] = ["dgmattribs.attributeID", False, None]
    #dgmattribs["chargeRechargeTimeID"] = ["dgmattribs.attributeID", False, None]
    dgmattribs["defaultValue"] = [None, False, None]
    dgmattribs["published"] = [None, False, None]
    dgmattribs["displayName"] = [None, False, None]
    dgmattribs["unitID"] = ["eveunits.unitID", False, None]
    dgmattribs["stackable"] = [None, False, None]
    dgmattribs["highIsGood"] = [None, False, None]
    #dgmattribs["categoryID"] = [None, False, None]
    dgmattribs["iconID"] = ["icons.iconID", False, None]

    dataspec["dgmeffects"] = [{}, False]
    dgmeffects = dataspec["dgmeffects"][0]
    dgmeffects["effectID"] = [None, False, None]
    dgmeffects["effectName"] = [None, False, None]
    dgmeffects["preExpression"] = ["dgmexpressions.expressionID", False, None]
    dgmeffects["postExpression"] = ["dgmexpressions.expressionID", False, None]
    dgmeffects["effectCategory"] = [None, False, None]
    #dgmeffects["description"] = [None, False, None]
    dgmeffects["isOffensive"] = [None, False, None]
    dgmeffects["isAssistance"] = [None, False, None]
    dgmeffects["durationAttributeID"] = ["dgmattribs.attributeID", False, None]
    dgmeffects["trackingSpeedAttributeID"] = ["dgmattribs.attributeID", False, None]
    dgmeffects["dischargeAttributeID"] = ["dgmattribs.attributeID", False, None]
    dgmeffects["rangeAttributeID"] = ["dgmattribs.attributeID", False, None]
    dgmeffects["falloffAttributeID"] = ["dgmattribs.attributeID", False, None]
    #dgmeffects["published"] = [None, False, None]
    dgmeffects["displayName"] = [None, False, None]
    #dgmeffects["isWarpSafe"] = [None, False, None]
    dgmeffects["fittingUsageChanceAttributeID"] = ["dgmattribs.attributeID", False, None]
    dgmeffects["iconID"] = ["icons.iconID", False, None]

    dataspec["dgmexpressions"] = [{}, False]
    dgmexpressions = dataspec["dgmexpressions"][0]
    dgmexpressions["expressionID"] = [None, False, None]
    dgmexpressions["operandID"] = [None, False, None]
    dgmexpressions["arg1"] = ["dgmexpressions.expressionID", False, None]
    dgmexpressions["arg2"] = ["dgmexpressions.expressionID", False, None]
    dgmexpressions["expressionValue"] = [None, False, None]
    dgmexpressions["expressionTypeID"] = ["invtypes.typeID", False, None]
    dgmexpressions["expressionGroupID"] = ["invgroups.groupID", False, None]
    dgmexpressions["expressionAttributeID"] = ["dgmattribs.attributeID", False, None]

    dataspec["dgmtypeattribs"] = [{}, False]
    dgmtypeattribs = dataspec["dgmtypeattribs"][0]
    dgmtypeattribs["typeID"] = ["invtypes.typeID", False, None]
    dgmtypeattribs["attributeID"] = ["dgmattribs.attributeID", False, None]
    dgmtypeattribs["value"] = [None, False, None]

    dataspec["dgmtypeeffects"] = [{}, False]
    dgmtypeeffects = dataspec["dgmtypeeffects"][0]
    dgmtypeeffects["typeID"] = ["invtypes.typeID", False, None]
    dgmtypeeffects["effectID"] = ["dgmeffects.effectID", False, None]
    dgmtypeeffects["isDefault"] = [None, False, None]

    dataspec["eveunits"] = [{}, False]
    eveunits = dataspec["eveunits"][0]
    eveunits["unitID"] = [None, False, None]
    #eveunits["unitName"] = [None, False, None]
    eveunits["displayName"] = [None, False, None]
    #eveunits["description"] = [None, False, None]

    dataspec["icons"] = [{}, False]
    icons = dataspec["icons"][0]
    icons["iconID"] = [None, False, None]
    icons["iconFile"] = [None, False, None]
    #icons["description"] = [None, False, None]
    #icons["iconType"] = [None, False, None]

    dataspec["invcategories"] = [{}, False]
    invcategories = dataspec["invcategories"][0]
    invcategories["categoryID"] = [None, False, None]
    invcategories["categoryName"] = [None, False, None]
    #invcategories["description"] = [None, False, None]
    #invcategories["published"] = [None, False, None]
    #invcategories["iconID"] = ["icons.iconID", False, None]

    dataspec["invgroups"] = [{}, False]
    invgroups = dataspec["invgroups"][0]
    invgroups["groupID"] = [None, False, None]
    invgroups["categoryID"] = ["invcategories.categoryID", False, None]
    invgroups["groupName"] = [None, False, None]
    invgroups["fittableNonSingleton"] = [None, False, None]
    #invgroups["description"] = [None, False, None]
    invgroups["published"] = [None, False, None]
    invgroups["iconID"] = ["icons.iconID", False, None]

    dataspec["invmarketgroups"] = [{}, False]
    invmarketgroups = dataspec["invmarketgroups"][0]
    invmarketgroups["parentGroupID"] = ["invmarketgroups.marketGroupID", False, None]
    invmarketgroups["marketGroupID"] = [None, False, None]
    invmarketgroups["marketGroupName"] = [None, False, None]
    #invmarketgroups["description"] = [None, False, None]
    invmarketgroups["hasTypes"] = [None, False, None]
    invmarketgroups["iconID"] = ["icons.iconID", False, None]

    dataspec["invmetagroups"] = [{}, False]
    invmetagroups = dataspec["invmetagroups"][0]
    invmetagroups["metaGroupID"] = [None, False, None]
    invmetagroups["metaGroupName"] = [None, False, None]
    #invmetagroups["description"] = [None, False, None]

    dataspec["invmetatypes"] = [{}, False]
    invmetatypes = dataspec["invmetatypes"][0]
    invmetatypes["typeID"] = ["invtypes.typeID", False, None]
    invmetatypes["parentTypeID"] = ["invtypes.typeID", False, None]
    invmetatypes["metaGroupID"] = ["invmetagroups.metaGroupID", False, None]

    dataspec["invtypes"] = [{}, True]
    invtypes = dataspec["invtypes"][0]
    invtypes["typeID"] = [None, False, None]
    invtypes["groupID"] = ["invgroups.groupID", False, None]
    invtypes["typeName"] = [None, False, None]
    invtypes["description"] = [None, False, None]
    invtypes["radius"] = [None, False, None]
    invtypes["mass"] = [None, False, None]
    invtypes["volume"] = [None, False, None]
    invtypes["capacity"] = [None, False, None]
    invtypes["raceID"] = [None, False, None]
    invtypes["published"] = [None, False, None]
    invtypes["marketGroupID"] = ["invmarketgroups.marketGroupID", False, None]
    invtypes["iconID"] = ["icons.iconID", False, None]

    dataspec["metadata"] = [{}, False]
    metadata = dataspec["metadata"][0]
    metadata["fieldName"] = [None, False, None]
    metadata["fieldValue"] = [None, False, None]

    # Data filter specification
    # ( table to clean, with column used as key, join statements, filter )
    filterspec = (("invtypes.typeID", "invtypes.groupID = invgroups.groupID | invgroups.categoryID = invcategories.categoryID", "invcategories.categoryName(Ship, Module, Charge, Skill, Drone, Implant, Subsystem) | invgroups.groupName(Effect Beacon)"),)

    # Additional exception specification, values from here won't be removed when there're no direct references to them
    # ( reference to keys of table for which we're making exception = values of the key to keep, additional condition, join statements )
    exceptspec = (("dgmattribs.attributeID = dgmtypeattribs.value", "eveunits.displayName = attributeID", "invtypes.typeID = dgmtypeattribs.typeID | dgmtypeattribs.attributeID = dgmattribs.attributeID | dgmattribs.unitID = eveunits.unitID"),
                  ("invgroups.groupID = dgmtypeattribs.value", "eveunits.displayName = groupID", "invtypes.typeID = dgmtypeattribs.typeID | dgmtypeattribs.attributeID = dgmattribs.attributeID | dgmattribs.unitID = eveunits.unitID"),
                  ("invtypes.typeID = dgmtypeattribs.value", "eveunits.displayName = typeID", "invtypes.typeID = dgmtypeattribs.typeID | dgmtypeattribs.attributeID = dgmattribs.attributeID | dgmattribs.unitID = eveunits.unitID"))

    return dataspec, filterspec, exceptspec

def get_source_data(sourcedata, table):
    """
    Pull data from the source data structure
    """
    # Temporary storage for data rows
    dictdatarows = []
    # Try dumb method of accessing header data (usually works for
    # IndexRowset, CIndexedRowset and FilterRowset)
    try:
        headobj = sourcedata.header
        # Sometimes header data represents itself row descriptor
        # (for CIndexedRowset), get actual list
        try:
            headers = headobj.Keys()
        # Use list itself if such data is unavailable
        except AttributeError:
            headers = headobj
        # For CIndexedRowsets, do some additional things
        else:
            # Reverse keys and values (it's in dbrow : key format)
            sourcedata = dict(zip(sourcedata.itervalues(),sourcedata.iterkeys()))
            # And raise error to go to recursive data seek
            raise AttributeError
    # Try something else (for structures like IndexedRowLists)
    except AttributeError:
        headers = []
        # IndexedRowLists structure may differ from table to table,
        # run recursion on it
        recursive_data_seek(sourcedata, headers, dictdatarows)
    # We got our headers, now get the data
    else:
        # Try to use efficient getter right away, should work for IndexRowset
        try:
            sourcedatalines = sourcedata.Select(*headers)
        # Other method for FilterRowsets
        except AttributeError:
            # Iterate through their keys
            for key in sourcedata.iterkeys():
                # Grab row sets
                rowset = sourcedata[key]
                rowsetdatalines = rowset.Select(*headers)
                # And process each data row
                for dataline in rowsetdatalines:
                    datarow = {}
                    for i in range(len(headers)):
                        datarow[headers[i]] = dataline[i]
                    dictdatarows.append(datarow)
        # Process data returned by getter
        else:
            for dataline in sourcedatalines:
                datarow = {}
                for i in range(len(headers)):
                    datarow[headers[i]] = dataline[i]
                dictdatarows.append(datarow)
    # Add columns into table object
    for header in headers:
        table.addcolumn(header)
    # Cycle through all the data we got
    for dictdatarow in dictdatarows:
        # Also convert ASCII strings to unicode using CCP's default encoding
        for k, v in dictdatarow.iteritems():
            if isinstance(v, str):
                dictdatarow[k] = unicode(v, "cp1252")
            # Also convert container data types to unicode string
            elif isinstance(v, (tuple, list, set)):
                dictdatarow[k] = u",".join(unicode(entry) for entry in v)
        # Convert it into tuples
        datarow = tuple(dictdatarow.get(column.name) for column in table.columns)
        # And add to the row set
        table.datarows.add(datarow)
    return

def recursive_data_seek(sourcedata, headerlist, datarows):
    """
    Recursively seek for data containers and pull data out of them
    """
    # Cycle through top-level data structure
    for iterentity in sourcedata:
        # Check if entities enclosed in it have header data
        try:
            headerdata = iterentity.__header__
        # If there's no such data, then we're dealing with dictionary keys
        except AttributeError:
            dictval = sourcedata[iterentity]
            # Check if these values have header data
            try:
                headerdata = dictval.__header__
            # If they don't, we're dealing with dictionary or list
            except AttributeError:
                # Let recursion run on it
                recursive_data_seek(dictval, headerlist, datarows)
            # Or pull data from dictionary value
            else:
                datarow = {}
                for header in headerdata.Keys():
                    datarow[header] = dictval[header]
                    if header not in headerlist:
                        headerlist.append(header)
                datarows.append(datarow)
        # If top-level data was list, get our data here
        else:
            datarow = {}
            for header in headerdata.Keys():
                datarow[header] = iterentity[header]
                if header not in headerlist:
                    headerlist.append(header)
            datarows.append(datarow)
    return

def detect_column_types(table):
    """
    Detect data type stored in columns of given table
    """
    # Bail if table has no data
    if len(table.datarows) == 0:
        return
    # Go through all columns of given table
    for column in table.columns:
        colidx = table.columns.index(column)
        # Assume the most limited data type by default
        datatype = BOOL
        # Cycle through data rows
        for datarow in table.datarows:
            # Get value for our column
            value = datarow[colidx]
            if value is None:
                continue
            # Boolean check
            if datatype <= BOOL:
                if isinstance(value, bool):
                    continue
                else:
                    datatype = INT
            # Integer check
            if datatype <= INT:
                if isinstance(value, int):
                    continue
                else:
                    datatype = FLOAT
            # Float check
            if datatype <= FLOAT:
                if isinstance(value, float):
                    continue
                else:
                    datatype = STR
                    # It can't be worse than string, so stop cycling
                    break
        # Write down results for current column
        column.datatype = datatype
    return

def detect_data_length(table):
    """
    Detect length of any given data type for each column
    """
    # Bail if table has no data
    if len(table.datarows) == 0:
        return
    # Iterate through all columns
    for column in table.columns:
        # We do not have any special restrictions on booleans or floats
        if column.datatype in (BOOL, FLOAT):
            continue
        colidx = table.columns.index(column)
        # Integer processing
        if column.datatype == INT:
            # Default min and max values are stored as Nones
            minval = None
            maxval = None
            # Just go through all data rows and find min/max values
            for datarow in table.datarows:
                value = datarow[colidx]
                if value is None:
                    continue
                if value < minval or minval is None:
                    minval = value
                if value > maxval or maxval is None:
                    maxval = value
            # Store them in the data length specificator
            column.datalen = (minval, maxval)
        # String processing
        elif column.datatype == STR:
            # Start from zero length for both  bytes and characters
            maxchars = 0
            maxbytes = 0
            # Go through all the data rows
            for datarow in table.datarows:
                value = datarow[colidx]
                if value is None:
                    continue
                # If value turned out to be not unicode, convert it
                if not isinstance(value, unicode):
                    value = unicode(value)
                # Get number of characters in the string
                valchars = len(value)
                # And overwrite maximum if it's over it
                if valchars > maxchars:
                    maxchars = valchars
                # Get number of bytes required to store string
                valbytes = len(value.encode("utf-8"))
                # Memorize it too, if it's higher than max
                if valbytes > maxbytes:
                    maxbytes = valbytes
            # Write data to column length specificator
            column.datalen = (maxchars, maxbytes)
    return

def detect_notnulls(table):
    """
    Check if any given column can be null
    """
    # Bail if table has no data
    if len(table.datarows) == 0:
        return
    # Iterate through all columns
    for column in table.columns:
        colidx = table.columns.index(column)
        # Assume that column doesn't have null values by default
        notnull = True
        # Iterate through all rows
        for datarow in table.datarows:
            value = datarow[colidx]
            # If it does, mark the result and break the loop
            if value is None:
                notnull = False
                break
        column.notnull = notnull
    return

def detect_uniques(table):
    """
    Check if column contains only unique values
    """
    # Bail if table has no data
    if len(table.datarows) == 0:
        return
    # Iterate through all columns
    for column in table.columns:
        colidx = table.columns.index(column)
        # Assume that column has unique values by default
        unique = True
        columndata = set()
        # Iterate through all rows
        for datarow in table.datarows:
            value = datarow[colidx]
            # Skip Nones as they're not considered when detecting uniqueness
            if value is None:
                continue
            # On first duplicate, mark the result and break the loop
            if value in columndata:
                unique = False
                break
            columndata.add(value)
        column.unique = unique
    return

def guess_primarykey(table):
    """
    Attempt to detect primary key columns of the table
    """
    # Bail if table has no data
    if len(table.datarows) == 0:
        return
    # Dictionary for PK candidates
    candidates = collections.OrderedDict()
    # Max score for any evaluation type
    POSITIONMAX = 100
    NAMEMAX = 200
    SEQUENCE = 200
    # Check all columns
    for column in table.columns:
        # Take only integers with some data in each row
        if column.datatype == INT and column.notnull is True:
            # Assign zero score
            candidates[column] = 0
    for column in candidates:
        # Do not process anything if we don't really need comparison
        if len(candidates) < 2:
            break
        colidx = table.columns.index(column)
        # Calculate position score
        # The farther to end of table, the less score
        maxindex = len(table.columns)-1
        positionscore = float(POSITIONMAX)*(maxindex-colidx)/(maxindex)
        candidates[column] += positionscore
        # Calculate name score
        # The more name of column looks like table name, the more score
        # ID suffix also adds some points
        namescore = 0
        idscore = float(NAMEMAX)/10
        maxmatchscore = NAMEMAX - idscore
        # If name ends with ID, add some
        if re.search("ID$", column.name):
            namescore += idscore
        simratio = get_similarity(table.name, re.sub("ID$", "", column.name))
        namescore += maxmatchscore * simratio
        candidates[column] += namescore
        # Check sequence quality, only for full-filled unique columns
        if column.unique is True and column.notnull is True:
            # Get all column data into single set
            columndata = set()
            for datarow in table.datarows:
                columndata.add(datarow[colidx])
            # Get start and end values of data
            start = min(columndata)
            end = max(columndata)
            # Number of entries which potentially can fit into [start, ..., end] range
            # For strictly positive sequences, consider that start is at 1
            fitrange = end - min((start, 1)) + 1
            # Sequence quality score multiplier, score is halved
            # if sequence starts from negative values
            seqmult = 1 if start >= 0 else 0.5
            sequencescore = float(SEQUENCE) * seqmult * len(columndata) / fitrange
            candidates[column] += sequencescore
    # Start from one column considered as primary key
    pks = 1
    # Set with columns which were confirmed as primary keys
    confirmedpks = set()
    # Number of columns considered as table primary
    # keys is changed between these cycles
    while(pks <= len(candidates)):
        # Get all possible combinations of given number of columns from candidates
        combinations = collections.OrderedDict()
        for combination in itertools.combinations(candidates.iterkeys(), pks):
            combinations[combination] = 0
            # Calculate total score for given combination
            for column in combination:
                combinations[combination] += candidates[column]
        # Arrange them into a tuple sorted by score, descending
        placement = tuple(sorted(combinations.iterkeys(), key=combinations.get, reverse=True))
        for combination in placement:
            if pks == 1:
                column = combination[0]
                if column.unique is True:
                    # Add it to confirmed key list
                    confirmedpks.add(column)
                    # Stop cycling through combinations
                    break
            else:
                # Will keep our temporary data
                data = set()
                # Assume this column combo can be used to address row
                canbepk = True
                for datarow in table.datarows:
                    # Get data for columns present in tested combination
                    datacomb = tuple(datarow[table.columns.index(column)] for column in combination)
                    # Any duplicate entry is unacceptable
                    if datacomb in data:
                        canbepk = False
                        break
                    data.add(datacomb)
                # If tested column combination is fine, fill the result
                if canbepk is True:
                    for column in combination:
                        confirmedpks.add(column)
            # Jump out of combination loop if we have the result
            if len(confirmedpks) > 0:
                break
        # Jump out of the outer loop too
        if len(confirmedpks) > 0:
            break
        # Increment number of minimal number of keyed columns
        pks += 1

    # Mark primary key columns
    for column in confirmedpks:
        column.pk = True
    # Mark the rest of the columns as non-primary keyed
    for column in set(table.columns).difference(confirmedpks):
        column.pk = False
    return

def get_similarity(one, two, ignorecase=True):
    """
    Compare 2 strings and return similarity ratio
    """
    # If we're asked to ignore case, make everything lower-cased
    if ignorecase is True:
        one = one.lower()
        two = two.lower()
    # Similarity ratio base value
    ratio = 0
    # Seek for longest full match
    matcher = difflib.SequenceMatcher(a=one, b=two)
    match = matcher.find_longest_match(0, len(one), 0, len(two))
    # Process matches which are longer than 3
    if match.size >= 3:
        fullbothlen = len(one) + len(two)
        # Longest full match gets full score
        fullscore = 2.0 * match.size / fullbothlen
        ratio += fullscore
        # Partial and shorter matches get partial score, 1/4
        partmult = 0.25
        # The ones before full match
        prebothlen = match.a + match.b
        preratio = difflib.SequenceMatcher(a=one[:match.a], b=two[:match.b]).ratio()
        prescore = partmult * prebothlen * preratio / fullbothlen
        ratio += prescore
        # And the ones after
        postbothlen = len(one) - match.a + len(two) - match.b - match.size * 2
        postratio = difflib.SequenceMatcher(a=one[match.a+match.size:], b=two[match.b+match.size:]).ratio()
        postscore = partmult * postbothlen * postratio / fullbothlen
        ratio += postscore
    return ratio

def remove_duplicate_tables(tables):
    """
    Remove tables with duplicate data
    """
    # Container for lists of duplicated tables
    dupetablegroups = []
    # Plain set for tables that were marked as duplicates
    dupes = set()
    # Iterate through all possible table combinations with 2 members
    for combination in itertools.combinations(tables.itervalues(), 2):
        table1 = combination[0]
        table2 = combination[1]
        # If both tables were checked already, go to the next combination
        if table1 in dupes and table2 in dupes:
            continue
        # Check if they possess the same data
        if table1.isduplicate(table2) is True:
            # If one of tables is already in set, we want to add it to existing group
            if table1 in dupes or table2 in dupes:
                # Cycle through groups
                for dupetablegroup in dupetablegroups:
                    # Find the one with table
                    if table1 in dupetablegroup or table2 in dupetablegroup:
                        # Add new table to group set and general set
                        dupetablegroup.add(table1)
                        dupes.add(table1)
                        dupetablegroup.add(table2)
                        dupes.add(table2)
                        break
            # If they were never reported as duplicate
            else:
                # Make new group
                dupetablegroups.append(set(combination))
                # And add both tables to general set
                dupes.add(table1)
                dupes.add(table2)
    # Now, when we detected all duplicate tables, go through all
    # duplicate groups and choose the survivor
    for dupetablegroup in dupetablegroups:
        candidates = collections.OrderedDict()
        for table in dupetablegroup:
            # Get lower-cased table name
            tablename = table.name.lower()
            # Get header primary key header names w/o ID suffix and make it lower-cased
            pks = list(re.sub("ID$", "", column.name).lower() for column in table.getpks())
            # Dictionary for the slices left after matches
            tablesliced = [tablename,]
            # Storage for matches
            matches = []
            # Go through all keys
            for pk in pks:
                # Match of maximum length for given key
                maxmatch = None
                # Index of source segment in slices list where max match occurred
                maxmatchsliceidx = None
                # Create new matcher object for each, setting key as cached string
                matcher = difflib.SequenceMatcher(b=pk)
                # Slice index starts from 0
                # We need to track it manually to properly support duplicate
                # data within the slice list
                sliceidx = 0
                # Iterate through slices
                for tableslice in tablesliced:
                    # Reuse matcher within loop, and set non-cached sequence here
                    matcher.set_seq1(tableslice)
                    # Find longest match using matcher
                    match = matcher.find_longest_match(0, len(tableslice), 0, len(pk))
                    # Ignore all matches less than 3 in size
                    if match.size >= 3:
                        # If we found bigger and better match, write it down
                        if maxmatch is None or match.size >= maxmatch.size:
                            maxmatch = match
                            maxmatchsliceidx = sliceidx
                    # Increment index manually
                    sliceidx += 1
                # If we got match that deserves our attention
                if maxmatch is not None:
                    # Slice'n'dice
                    slicesrc = tablesliced[maxmatchsliceidx]
                    # Matching part
                    slicematch = slicesrc[maxmatch.a:maxmatch.a+maxmatch.size]
                    # Parts of table name slice before and after match
                    tablepre = slicesrc[:maxmatch.a]
                    tablepost = slicesrc[maxmatch.a+maxmatch.size:]
                    # Add match to list of matches
                    matches.append(slicematch)
                    # Replace source slice by pre-match
                    tablesliced[maxmatchsliceidx] = tablepre
                    # Insert post-match right after it
                    tablesliced.insert(maxmatchsliceidx+1, tablepost)
            # Length of all primary keys
            pkslen = sum(len(pk) for pk in pks)
            # Same for matches
            matcheslen = sum(len(match) for match in matches)
            # Score multiplier
            mult = 1.0
            for tableslice in tablesliced:
                # If there's "by" in table name remnants, halve score
                # CCP usually adds them to alternatively sorted tables with the same contents
                if "by" in tableslice:
                    mult = 0.5
                    break
            candidates[table] = mult * matcheslen / (len(table.name) + pkslen)
        # The winner takes it all
        winner = max(candidates, key=candidates.get)
        # Losers die
        for table in dupetablegroup:
            if table != winner:
                print("  Removed table {0} in favor of {1}".format(table.name, winner.name))
                del tables[table.name]
    return

def database_refactor(tables, dbspec, filterspec, exceptspec):
    """
    Refactor database according to passed specification
    """
    # Gather number of data rows for statistics
    rowlen = {}
    for tabname in tables:
        rowlen[tabname] = len(tables[tabname].datarows)

    ## STAGE 1: here we make database specification structure and
    ## actual database consistent, performing series of checks and
    ## removing data which isn't reflected in other entity. Also here
    ## we fill in-script database representation structure with several
    ## column flags (FK, indices) and do some auxiliary stuff for further
    ## stages
    # Just error flag, used for user's convenience
    specerrors = False
    # Detect non-existing tables
    tab404 = set(dbspec.iterkeys()).difference(tables.iterkeys())
    # If we found any
    if len(tab404) > 0:
        # Remove them from specification container
        for tabname in tab404:
            del dbspec[tabname]
        # And inform about it
        plu = "" if len(tab404) == 1 else "s"
        tab404names = ", ".join(sorted(tab404))
        print("  Unable to find specified table{0}: {1}".format(plu, tab404names))
        # Set error flag to True
        specerrors = True
    # Get set of tables to be removed and get rid of them
    toremove = set(tables.iterkeys()).difference(set(dbspec.iterkeys()))
    for tabname in toremove:
        del tables[tabname]
    # Cycle through remaining tables, sort them for alphabetic table
    # name sorting in case of any errors, this doesn't matter otherwise
    for tabname in sorted(dbspec.iterkeys()):
        table = tables[tabname]
        actcolnames = set(col.name for col in table.columns)
        specolnames = set(dbspec[tabname][0].iterkeys())
        # Detect non-existing columns
        col404 = specolnames.difference(actcolnames)
        # If we've got such columns
        if len(col404) > 0:
            # Remove them from specification
            for col in col404:
                del dbspec[tabname][0][col]
            # Tell user about it
            plu = "" if len(col404) == 1 else "s"
            col404names = ", ".join(sorted(col404))
            print("  Unable to find specified column{0} for table {1}: {2}".format(plu, tabname, col404names))
            # Set error flag to True
            specerrors = True
        # Finally, get rid of unneeded columns
        toremove = actcolnames.difference(dbspec[tabname][0].iterkeys())
        problems = table.removecolumns(toremove)
        # If we had any errors during column  removal, set error flag
        if problems is True:
            specerrors = True
    # Local data structures to store FK relations
    # 1:1 source-target relation
    # { source table : { source column : target } }
    src_fk_tgt = {}
    # 1:many target-source relation
    # { target table : { target column : sources } }
    tgt_fk_src = {}
    # Fill foreign key references for all columns according to specification
    # As our data/specification structures are now 'synchronized', we can go
    # through any of them - here we picked data as it's faster and more convenient
    for tabname in tables:
        table = tables[tabname]
        for column in table.columns:
            # Get FK specification string
            fkspec = dbspec[table.name][0][column.name][0]
            # If it's None, ignore current column
            if fkspec is None:
                continue
            # Source data column must be integer
            if column.datatype != INT:
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
            if not fktabname in tables or tables[fktabname].getcolumn(fkcolname) is None:
                print("  Unable to find foreign key target for {0}.{1} ({2}.{3})".format(table.name, column.name, fktabname, fkcolname))
                specerrors = True
                continue
            fktable = tables[fktabname]
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

    # Set index flags for all appropriate columns
    indexerrors = set()
    for tabname in sorted(dbspec.iterkeys()):
        for colname in dbspec[tabname][0]:
            idxize = dbspec[tabname][0][colname][1]
            if idxize is True or idxize is False:
                tables[tabname].getcolumn(colname).index = idxize
            # Print error on unexpected values
            else:
                print("  Corrupted index data for {0}.{1}".format(tabname, colname))

    # Print reminder in case of any errors
    if specerrors is True:
        print("  Please revise data specification")

    # Dictionaries to track number of removed rows per table
    rmvd_filter = {}
    rmvd_brokenref = {}
    rmvd_norefto = {}
    # Fill them with zeros for all tables by default
    for tabname in tables:
        rmvd_filter[tabname] = 0
        rmvd_brokenref[tabname] = 0
        rmvd_norefto[tabname] = 0

    ## STAGE 2: remove data according to provided specification
    # Storage for data which was filtered out
    # { table : set(data rows) }
    filteredout = {}

    # Run table data filters
    for filter in filterspec:
        success = table_filter(tables, filter, rmvd_filter, filteredout)
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
    for tabname in dbspec:
        table = tables[tabname]
        # All their columns
        for colname in dbspec[tabname][0]:
            # Check exceptions section
            excspec = dbspec[tabname][0][colname][2]
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
        for exc in exceptspec:
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
                if not tabname in tables:
                    print("  Unable to find table specified in exception definition: {0}".format(tabname))
                    errexcspecs.add(exc)
                    break
                if tables[tabname].getcolumn(colname) is None:
                    print("  Unable to find column of table {0} specified in exception definition: {1}".format(tabname, colname))
                    errexcspecs.add(exc)
                    break
            if exc in errexcspecs:
                excerrors = True
                continue
            # Start doing actual job; join columns as stated in join statement set
            success, joinedcols, joinedrows = table_join(tables, joinspec)
            # Bail in case of any errors, as usual
            if success is not True:
                excerrors = True
                errexcspecs.add(exc)
                continue
            # Get index of the column by which we're going to filer
            excfiltabname = filtertabcol.split(".")[0]
            excfilcolname = filtertabcol.split(".")[1]
            try:
                excfilidx = joinedcols.index(tables[excfiltabname].getcolumn(excfilcolname))
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
                excsrcidx = joinedcols.index(tables[excsrctabname].getcolumn(excsrccolname))
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
            exctgtcolidx = tables[exctgttabname].columns.index(tables[exctgttabname].getcolumn(exctgtcolname))
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
                tables[tabname].datarows.update(putback)
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
                    coldata[key] = tables[tabname].getcolumndataset(colname)
        # Then with data for columns which are referenced by other columns
        for tabname in tgt_fk_src:
            for colname in tgt_fk_src[tabname]:
                key = "{0}.{1}".format(tabname, colname)
                if not key in coldata:
                    coldata[key] = tables[tabname].getcolumndataset(colname)
        # Go through data container and remove zero from every set, as
        # CCP seem to set zeros in some cases when they should've set None
        for column in coldata:
            coldata[column].difference_update({0})
        # Do actual cleaning
        for tabname in tables:
            table = tables[tabname]
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
            tabstrength = dbspec[tabname][1]
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
    for tabname in sorted(tables.iterkeys()):
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

def table_filter(tables, rmspec, statsdict, filteredout):
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
    success, joinedcols, joinedrows = table_join(tables, joinspec)
    # If we had some errors during join, just bail
    if success is not True:
        return False

    # Now, when we have our joined table ready, start filtering jobs
    # Use this data structure to hold filter data
    # { filter column index : set(acceptable filter values) }
    filters = {}
    # Go through all filters separated by OR sign
    for filter in filterspec.split("|"):
        # Use regexp for matching
        match = re.search("([\w]+\.[\w]+)\(([\w ]+(,[\w ]+)*)\)", filter)
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
        for filter in filters:
            # If we find match, note down to keep this row and break
            # iteration over filters
            if row[filter] in filters[filter]:
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

def table_join(tables, joinspec):
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

def dump_sqlite(tables, path):
    """
    Dump everything we've got into SQLite file
    """
    # Check if dump file already exists and remove it
    if os.path.exists(path):
        os.remove(path)

    # Connect to SQLite dump database
    conn = sqlite3.connect(path)
    c = conn.cursor()

    # Data type specification for SQLite
    datatypes = { BOOL : "INTEGER",
                  INT : "INTEGER",
                  FLOAT : "REAL",
                  STR : "TEXT" }

    # For each table
    for tablename in sorted(tables):
        table = tables[tablename]
        # Skip tables with no data
        if len(table.datarows) == 0:
            continue
        # First, compose list of PK'ed columns
        pks = table.getpks()
        # Now get data regarding each column
        tablecolumns = []
        for column in table.columns:
            columnspec = []
            # We need column name in first place
            columnspec.append(u"\"{0}\"".format(column.name))
            # Then, data type
            columnspec.append(datatypes[column.datatype])
            # If this column is single PK, specify it here
            if column.pk is True and len(pks) == 1:
                columnspec.append("PRIMARY KEY")
            # Not null is added when column is not null and it's
            # not single primary key in table
            if column.notnull is True and (column.pk is not True or len(pks) > 1):
                columnspec.append("NOT NULL")
            # Data uniqueness is specified if column is not a PK
            if column.unique is True and column.pk is not True:
                columnspec.append("UNIQUE")
            # Add foreign key constraint
            if column.fk is not None:
                tabname, colname = column.fk.split(".")
                columnspec.append(u"REFERENCES \"{0}\"(\"{1}\")".format(tabname, colname))
            # Aggregate all data into single string
            tablecolumns.append(" ".join(columnspec))
        # Specify primary keys for whole table, if there're multiple PKs
        if len(pks) > 1:
            tablecolumns.append(u"PRIMARY KEY ({0})".format(u", ".join(u"\"{0}\"".format(pk.name) for pk in pks)))
        # Create table in the database
        columnspec = u", ".join(tablecolumns)
        statement = u"CREATE TABLE \"{0}\" ({1})".format(table.name, columnspec)
        c.execute(statement)
        # Process table indices
        for idxcol in table.getindices():
            statement = u"CREATE INDEX \"ix_{0}_{1}\" ON \"{0}\" (\"{1}\")".format(table.name, idxcol.name)
            c.execute(statement)
        # Fill it with data
        datarows = table.datarows
        # Sort by PKs
        for pk in reversed(pks):
            datarows = sorted(datarows, key=lambda row: row[table.columns.index(pk)])
        # Fill the table with actual data
        statement = u"INSERT INTO {0} VALUES ({1})".format(table.name, ", ".join("?" for column in table.columns))
        c.executemany(statement, datarows)
    # Cleanup jobs
    conn.commit()
    c.execute("VACUUM")
    c.close()
    conn.close()
    return

def dump_mysql(tables, path):
    """
    Dump everything we've got into MySQL statements file
    """
    # Define conversion map for strings and compile regexp from it
    # It will be used later
    convmap = {"\0" : "\\0",
               "'" : "\\'",
               "\"" : "\\\"",
               "\b" : "\\b",
               "\n" : "\\n",
               "\r" : "\\r",
               "\t" : "\\t",
               "\x1A" : "\\Z",
               "\\" : "\\\\",
               "%" : "\\%",
               "_" : "\\_"}
    convre = re.compile("|".join(map(re.escape, convmap)))
    # We'll gradually write stuff to file, so open it
    f = codecs.open(path, encoding="utf-8", mode="w")
    # Cycle through tables
    for tablename in sorted(tables):
        table = tables[tablename]
        # Skip tables with no data
        if len(table.datarows) == 0:
            continue
        # Container for whole table definitions
        tabdefs = []
        # To avoid some manual work, drop existing table
        tabdefs.append(u"DROP TABLE IF EXISTS `{0}`;".format(table.name))
        # And start creating it
        tabdefs.append(u"CREATE TABLE `{0}` (".format(table.name))
        # Container for definition of all columns
        coldefs = []
        # Fill it, going through all of them
        for column in table.columns:
            # Container for definition of single column
            colspec = []
            # First, get the column name into there
            colspec.append(u"`{0}`".format(column.name))
            # Now, detect types
            # Booleans are straight
            if column.datatype == BOOL:
                colspec.append("TINYINT")
            # Integers are a bit more complex
            elif column.datatype == INT:
                # Unpack data length first
                minval, maxval = column.datalen
                # Use this block for signed integers
                if minval < 0:
                    # Subsequently check ranges to see if our numbers fit into it
                    if minval >= -(2 ** 7) and maxval <= (2 ** 7) - 1:
                        colspec.append("TINYINT")
                    elif minval >= -(2 ** 15) and maxval <= (2 ** 15) - 1:
                        colspec.append("SMALLINT")
                    elif minval >= -(2 ** 23) and maxval <= (2 ** 23) - 1:
                        colspec.append("MEDIUMINT")
                    elif minval >= -(2 ** 31) and maxval <= (2 ** 31) - 1:
                        colspec.append("INT")
                    else:
                        colspec.append("BIGINT")
                # Unsigned integers
                else:
                    if maxval <= (2 ** 8) - 1:
                        colspec.append("TINYINT")
                    elif maxval <= (2 ** 16) - 1:
                        colspec.append("SMALLINT")
                    elif maxval <= (2 ** 24) - 1:
                        colspec.append("MEDIUMINT")
                    elif maxval <= (2 ** 32) - 1:
                        colspec.append("INT")
                    else:
                        colspec.append("BIGINT")
                    # Let MySQL know that integer is unsigned
                    colspec.append("UNSIGNED")
            # Floats are straight too
            elif column.datatype == FLOAT:
                colspec.append("DOUBLE")
            # String is also complex
            elif column.datatype == STR:
                # Unpack length info
                maxchars, maxbytes = column.datalen
                # Varchar can fit max 65535 bytes
                if maxbytes <= (2 ** 16) - 1:
                    # But it's length specificator uses characters
                    colspec.append("VARCHAR({0})".format(maxchars))
                # Store everything else as text of appropriate length
                elif maxbytes <= (2 ** 24) - 1:
                    colspec.append("MEDIUMTEXT")
                else:
                    colspec.append("LONGTEXT")
            # Also store not-null specifications
            if column.notnull is True:
                colspec.append("NOT NULL")
            # And unique
            if column.unique is True:
                colspec.append("UNIQUE")
            # Combine everything regarding current column and add to general column storage
            coldefs.append(" ".join(colspec))
        # Tuple of primary keys
        pks = table.getpks()
        # Add primary key line
        if len(pks) > 0:
            coldefs.append(u"PRIMARY KEY ({0})".format(u",".join(u"`{0}`".format(c.name) for c in pks)))
        # Same for foreign keys
        fks = table.getfks()
        for fkcol in fks:
            fktabname, fkcolname = fkcol.fk.split(".")
            coldefs.append(u"FOREIGN KEY (`{0}`) REFERENCES `{1}` (`{2}`)".format(fkcol.name, fktabname, fkcolname))
        # Merge all table column definitions into single string
        tabdefs.append(u"  {0}".format(u",\n  ".join(coldefs)))
        # Finally, close table definition
        tabdefs.append(u") ENGINE = MyISAM DEFAULT CHARACTER SET = utf8;".format(table.name))
        # And write it to file
        f.write(u"{0}\n".format(u"\n".join(tabdefs)))
        # Process table indices
        for idxcol in table.getindices():
            f.write(u"CREATE INDEX `ix_{0}_{1}` ON `{0}` (`{1}`);\n".format(table.name, idxcol.name))
        f.write("\n")
        # We'll start write our data from here, from locking table for writing
        f.write(u"LOCK TABLES `{0}` WRITE;\n".format(table.name))
        # To avoid performance problems, disable autocommit
        f.write("SET autocommit = 0;\n")
        # Sort by PKs
        datarows = table.datarows
        for pk in reversed(pks):
            datarows = sorted(datarows, key=lambda row: row[table.columns.index(pk)])
        # Insert actual data, cycling through data rows
        for datarow in datarows:
            # Get all data for a row into single list
            rowdata = []
            # Go through all row fields
            for field in datarow:
                # Convert Nones into NULLs
                if field is None:
                    rowdata.append("NULL")
                # Do extra processing for strings
                if isinstance(field, basestring):
                    # Replace all text according to replacement map, quote and add to the list
                    rowdata.append(u"'{0}'".format(convre.sub(lambda match: convmap[match.group(0)], field)))
                # For everything else, just convert to text and add to list
                else:
                    rowdata.append(unicode(field))
            # Finally, write data row into the file
            f.write(u"INSERT INTO `{0}` VALUES ({1});\n".format(table.name, u",".join(rowdata)))
        # As we're done, unlock table
        f.write("UNLOCK TABLES;\n".format(table.name))
        # And run manual commit
        f.write("COMMIT;\n\n".format(table.name))
    # Cleanup jobs
    f.close()
    return

if __name__ == "__main__":
    # Check python version first (some parts of script and reverence require 2.7)
    import sys
    try:
        major = sys.version_info.major
        minor = sys.version_info.minor
    except AttributeError:
        major = sys.version_info[0]
        minor = sys.version_info[1]
    if major != 2 or minor < 7:
        sys.stderr.write("This application requires Python 2.7 to run, but {0}.{1} was used\n".format(major, minor))
        sys.exit()

    import codecs
    import collections
    import difflib
    import itertools
    import os.path
    import re
    import sqlite3
    from ConfigParser import ConfigParser
    from optparse import OptionParser

    from reverence import blue

    from data import Table

    # Parse command line options
    usage = "usage: %prog --eve=EVE --cache=CACHE --dump=DUMP [--sisi] [--release=RELEASE]"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--eve", help="path to eve folder")
    parser.add_option("-c", "--cache", help="path to eve cache folder")
    parser.add_option("-l", "--sqlite", help="path to SQLite dump file, including file name")
    parser.add_option("-m", "--mysql", help="path to MySQL dump file, including file name")
    parser.add_option("-s", "--sisi", action="store_true", dest="singularity", help="if you're going to work with Singularity test server data, use this option", default=False)
    parser.add_option("-r", "--release", help="database release number, defaults to 1", default="1")
    parser.add_option("-f", "--filter", action="store_true", help="enable data filtering for Eos", default=False)
    (options, args) = parser.parse_args()

    # Exit if we do not have any of required options
    if not options.eve or not options.cache or not (options.sqlite or options.mysql):
        sys.stderr.write("You need to specify paths to eve folder, cache folder and dump file. Run script with --help option for further info.\n")
        sys.exit()

    # We can deal either with singularity or tranquility servers
    if options.singularity: server = "singularity"
    else: server = "tranquility"

    # Set static variables for paths
    PATH_EVE = os.path.expanduser(options.eve)
    PATH_CACHE = os.path.expanduser(options.cache)

    # Initialize Reverence cache manager
    try:
        eve = blue.EVE(PATH_EVE, cachepath=PATH_CACHE, server=server)
    except RuntimeError:
        sys.stderr.write("Unable to find EVE cache or it's corrupted, please log into EVE to fix this.\n")
        sys.exit()
    cfg = eve.getconfigmgr()

    # List of data types, sorted by ability to store data
    BOOL = 1
    INT = 2
    FLOAT = 3
    STR = 4

    # Dictionary with data for custom tables, which are not generally available in cache
    customtables = { "dgmoperands":
                         (eve.RemoteSvc('dogma').GetOperandsForChar,
                          "dogma operands data is unavailable"),
                     "invmarketgroups":
                         (eve.RemoteSvc("marketProxy").GetMarketGroups,
                          "market tree data is unavailable; to cache it, open Browse tab of EVE market browser") }

    # Container for tables
    tables = collections.OrderedDict()

    print("Getting data from EVE Client")
    for tablename in itertools.chain(cfg.tables, customtables.iterkeys()):
        # Create new table object and add it to our table map
        table = Table(tablename)
        tables[tablename] = table
        # Get source data object from reverence
        try:
            srcdata = getattr(cfg, tablename)
        except AttributeError:
            try:
                srcdata = customtables[tablename][0]()
            except IOError:
                print("Warning: processing table {0} failed: {1}.".format(tablename, customtables[tablename][1]))
                continue
            except:
                sys.stderr.write("Error: unable to get data for one of the tables, most likely due to wrong path to EVE client.\n")
                sys.exit()
        except TypeError:
            sys.stderr.write("Error: unable to get data for one of the tables, most likely due to wrong path to EVE client.\n")
            sys.exit()
        # Get all the data from it
        get_source_data(srcdata, table)
        # Notify if there was no data in processed table
        if len(table.datarows) == 0:
            print("  Table {0} has no data rows".format(table.name))

    # Compose metadata table; first, read client version
    config = ConfigParser()
    config.read(os.path.join(PATH_EVE, "common.ini"))
    # Convert it to Unicode to make sure columns are detected as text
    evever = unicode(config.getint("main", "build"))
    # Create table object itself
    metatable = Table("metadata")
    # Add columns to it
    metatable.addcolumn("fieldName")
    metatable.addcolumn("fieldValue")
    # Add data
    metatable.datarows.add(("version", evever))
    metatable.datarows.add(("release", options.release))
    # Append table object to tables dictionary
    if not metatable.name in tables:
        tables[metatable.name] = metatable
    else:
        print("Warning: unable to add metadata table, table with this name already exists")

    print("Detecting columns data format")
    for table in tables.itervalues():
        # Detect types of columns
        detect_column_types(table)
        # Max length of data for each column
        detect_data_length(table)
        # Detect if columns can be nulls and if they have only unique values
        detect_notnulls(table)
        detect_uniques(table)

    print("Detecting primary keys")
    for table in tables.itervalues():
        # Detect primary key for each table
        guess_primarykey(table)

    # Remove the data we don't need
    if options.filter is True:
        # Manual mode: remove the data we don't need according to specification
        print("Refactoring database")
        database_refactor(tables, *get_eosdataspec())
    else:
        # Automatic mode: eve cache contains structures with the same actual data,
        # but differently grouped, so we're going to remove duplicates. This method
        # relies on table names and PK names, thus must be placed after PK detection
        print("Removing duplicate tables")
        remove_duplicate_tables(tables)

    # Write data to disk
    if options.sqlite:
        print("Writing SQLite dump")
        dump_sqlite(tables, os.path.expanduser(options.sqlite))
    if options.mysql:
        print("Writing MySQL dump")
        dump_mysql(tables, os.path.expanduser(options.mysql))
