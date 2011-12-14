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

    import os.path
    from optparse import OptionParser

    from data import EveDB
    from processing import DataMiner, Preprocessor, Deduplicator, EosAdapter, Dumper

    # Parse command line options
    usage = "usage: %prog --eve=EVE --cache=CACHE --dump=DUMP [--sisi] [--release=RELEASE] [--eos]"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--eve", help="path to eve folder")
    parser.add_option("-c", "--cache", help="path to eve cache folder")
    parser.add_option("-l", "--sqlite", help="path to SQLite dump file, including file name")
    parser.add_option("-m", "--mysql", help="path to MySQL dump file, including file name")
    parser.add_option("-s", "--sisi", action="store_true", dest="singularity", help="if you're going to work with Singularity test server data, use this option", default=False)
    parser.add_option("-r", "--release", help="database release number, defaults to 1", default="1")
    parser.add_option("-o", "--eos", action="store_true", help="enable data refactoring for Eos", default=False)
    parser.add_option("-d", "--eosold", action="store_true", help="enable data refactoring for old Eos", default=False)
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

    # Container for tables
    evedb = EveDB()

    # Create data miner and run it, pulling all the data from cache
    print("Getting data from EVE Client")
    dataminer = DataMiner(evedb, PATH_EVE, PATH_CACHE, server, options.release)
    dataminer.run()

    # Some data processing
    if options.eos is True:
        # Manual mode: refactor database format to make it suitable for eos needs,
        # remove data not needed and detect type of remaining
        print("Refactoring database for Eos")
        adapter = EosAdapter(evedb)
        adapter.run()
    elif options.eosold is True:
        # Manual mode: refactor database format to make it suitable for eos needs,
        # remove data not needed and detect type of remaining
        print("Refactoring database for old Eos")
        adapter = EosAdapter(evedb)
        adapter.run_old()
    else:
        # Automatic mode
        # Create preprocessor and find out some metadata for our tables
        print("Detecting columns data format")
        preprocessor = Preprocessor(evedb)
        preprocessor.run()
        # Eve cache contains structures with the same actual data,
        # but differently grouped, so we're going to remove duplicates. This method
        # relies on table names and PK names, thus must be placed after PK detection
        print("Removing duplicate tables")
        deduplicator = Deduplicator(evedb)
        deduplicator.run()

    # Create dumper object to write data to actual files
    dumper = Dumper(evedb)
    if options.sqlite:
        print("Writing SQLite dump")
        dumper.sqlite(os.path.expanduser(options.sqlite))
    if options.mysql:
        print("Writing MySQL dump")
        dumper.mysql(os.path.expanduser(options.mysql))
