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

class Deduplicator(object):
    """
    Handle removal of tables with duplicate data
    """
    def __init__(self, tables):
        self.tables = tables

    def run(self):
        print("Removing duplicate tables")
        deathgroups = self.__get_deathgroups()
        for deathgroup in deathgroups:
            self.__kill_losers(deathgroup)
        return

    def __get_deathgroups(self):
        """Find tables with duplicate data and return them as list of dupe lists"""
        # Container for lists of duplicated tables
        deathgroups = []
        # Plain set for tables that were marked as duplicates
        dupes = set()
        # Iterate through all possible table combinations with 2 members
        for combination in itertools.combinations(self.tables.itervalues(), 2):
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
                    for dupetablegroup in deathgroups:
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
                    deathgroups.append(set(combination))
                    # And add both tables to general set
                    dupes.add(table1)
                    dupes.add(table2)
        return deathgroups

    def __kill_losers(self, deathgroup):
        """Remove tables which turn to be worse than their group mates"""
        # Go through death group and choose the survivor
        candidates = collections.OrderedDict()
        for table in deathgroup:
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
        for table in deathgroup:
            if table != winner:
                print("  Removed table {0} in favor of {1}".format(table.name, winner.name))
                del self.tables[table.name]
        return
