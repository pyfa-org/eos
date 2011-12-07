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

import itertools
import os.path
import sys
from ConfigParser import ConfigParser

from reverence import blue

from data import Table

class DataMiner(object):
    """
    Class responsible for getting data out of EVE client
    """
    def __init__(self, tables, evepath, cachepath, server, release):
        # Will be used by other components in other methods
        self.evepath = evepath
        self.release = release
        # Initialize Reverence cache manager
        try:
            self.eve = blue.EVE(evepath, cachepath=cachepath, server=server)
        except RuntimeError:
            sys.stderr.write("Unable to find EVE cache or it's corrupted, please log into EVE to fix this.\n")
            sys.exit()
        self.cfg = self.eve.getconfigmgr()
        # Set storage container for tables
        self.tables = tables

    def run(self):
        """Controls actual data mining workflow"""
        # Assign to local variables for ease of use
        eve = self.eve
        cfg = self.cfg
        # Dictionary with data for custom tables, which are not generally available in cache
        customtables = {"dgmoperands":
                            (eve.RemoteSvc('dogma').GetOperandsForChar,
                             "dogma operands data is unavailable"),
                        "invmarketgroups":
                            (eve.RemoteSvc("marketProxy").GetMarketGroups,
                             "market tree data is unavailable; to cache it, open Browse tab of EVE market browser") }
        print("Getting data from EVE Client")
        for tablename in itertools.chain(cfg.tables, customtables.iterkeys()):
            # Create new table object
            table = Table(tablename)
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
            self.__get_source_data(srcdata, table)
            # Notify if there was no data in processed table
            if len(table.datarows) == 0:
                print("  Table {0} has no data rows".format(table.name))
            # Add table to our table map only if there's something in it
            else:
                self.tables[tablename] = table
        # Create metadata table
        self.__add_metadata()
        return

    def __get_source_data(self, sourcedata, table):
        """Pull data from the source data structure"""
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
            self.__recursive_data_seek(sourcedata, headers, dictdatarows)
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

    def __recursive_data_seek(self, sourcedata, headerlist, datarows):
        """Recursively seek for data containers and pull data out of them"""
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
                    self.__recursive_data_seek(dictval, headerlist, datarows)
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

    def __add_metadata(self):
        """Adds metadata table to table structure"""
        # Compose metadata table; first, read client version
        config = ConfigParser()
        config.read(os.path.join(self.evepath, "common.ini"))
        # Convert it to Unicode to make sure columns are detected as text
        evever = unicode(config.getint("main", "build"))
        # Create table object itself
        metatable = Table("metadata")
        # Add columns to it
        metatable.addcolumn("fieldName")
        metatable.addcolumn("fieldValue")
        # Add data
        metatable.datarows.add(("version", evever))
        metatable.datarows.add(("release", self.release))
        # Append table object to tables dictionary
        if not metatable.name in self.tables:
            self.tables[metatable.name] = metatable
        else:
            print("Warning: unable to add metadata table, table with this name already exists")
        return
