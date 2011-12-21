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
import difflib
import itertools
import re

from eve2sql import const

class Preprocessor(object):
    """
    Handle preliminary data processing
    """
    def __init__(self, evedb):
        self.evedb = evedb

    def run(self):
        for table in self.evedb:
            # Detect types of columns
            self.__detect_column_types(table)
            # Max length of data for each column
            self.__detect_data_length(table)
            # Detect if columns can be nulls and if they have only unique values
            self.__detect_notnulls(table)
            self.__detect_uniques(table)
            # Detect primary key for each table
            self.__guess_primarykey(table)
        return

    def __detect_column_types(self, table):
        """Detect data type stored in columns of given table"""
        # Go through all columns of given table
        for column in table:
            colidx = table.index(column)
            # Assume the most limited data type by default
            datatype = const.type_BOOL
            # Cycle through data rows
            for datarow in table.datarows:
                # Get value for our column
                value = datarow[colidx]
                if value is None:
                    continue
                # Boolean check
                if datatype <= const.type_BOOL:
                    if isinstance(value, bool):
                        continue
                    else:
                        datatype = const.type_INT
                # Integer check
                if datatype <= const.type_INT:
                    if isinstance(value, int):
                        continue
                    else:
                        datatype = const.type_FLOAT
                # Float check
                if datatype <= const.type_FLOAT:
                    if isinstance(value, float):
                        continue
                    else:
                        datatype = const.type_STR
                        # It can't be worse than string, so stop cycling
                        break
            # Write down results for current column
            column.datatype = datatype
        return

    def __detect_data_length(self, table):
        """Detect length of any given data type for each column"""
        # Iterate through all columns
        for column in table:
            # We do not have any special restrictions on booleans or floats
            if column.datatype in (const.type_BOOL, const.type_FLOAT):
                continue
            colidx = table.index(column)
            # Integer processing
            if column.datatype == const.type_INT:
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
            elif column.datatype == const.type_STR:
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

    def __detect_notnulls(self, table):
        """Check if any given column can be null"""
        # Iterate through all columns
        for column in table:
            colidx = table.index(column)
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

    def __detect_uniques(self, table):
        """Check if column contains only unique values"""
        # Iterate through all columns
        for column in table:
            colidx = table.index(column)
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

    def __guess_primarykey(self, table):
        """Attempt to detect primary key columns of the table"""
        # Dictionary for PK candidates
        candidates = collections.OrderedDict()
        # Max score for any evaluation type
        POSITIONMAX = 100
        NAMEMAX = 200
        SEQUENCE = 200
        # Check all columns
        for column in table:
            # Take only integers with some data in each row
            if column.datatype == const.type_INT and column.notnull is True:
                # Assign zero score
                candidates[column] = 0
        for column in candidates:
            # Do not process anything if we don't really need comparison
            if len(candidates) < 2:
                break
            colidx = table.index(column)
            # Calculate position score
            # The farther to end of table, the less score
            maxindex = len(table)-1
            positionscore = float(POSITIONMAX) * (maxindex - colidx) / (maxindex)
            candidates[column] += positionscore
            # Calculate name score
            # The more name of column looks like table name, the more score
            # ID suffix also adds some points
            namescore = 0
            idscore = float(NAMEMAX) / 10
            maxmatchscore = NAMEMAX - idscore
            # If name ends with ID, add some
            if re.search("ID$", column.name):
                namescore += idscore
            simratio = self.__get_similarity(table.name, re.sub("ID$", "", column.name))
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
                        datacomb = tuple(datarow[table.index(column)] for column in combination)
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
        for column in set(table).difference(confirmedpks):
            column.pk = False
        return

    def __get_similarity(self, one, two, ignorecase=True):
        """Compare 2 strings and return similarity ratio"""
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
