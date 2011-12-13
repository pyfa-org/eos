#!/usr/bin/env python3
#===============================================================================
# Copyright (C) 2011 Anton Vorobyov
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
Rebuild icons for UI needs. Script makes use of imagemagick and shell pipes.
"""

ICON_SIZE = 16
RENDERS_SIZE = 32

import argparse
import os
import re
import shutil
import sqlite3
import sys

parser = argparse.ArgumentParser(description="Rebuild icons for UI needs")
parser.add_argument("-d", "--dump", type=str, help="path to SQLite data dump")
parser.add_argument("-i", "--images", type=str, help="path to folder with unpacked source image data")
parser.add_argument("-o", "--output", type=str, help="path to folder where to store result")
args = parser.parse_args()

if args.dump is None or args.images is None or args.output is None:
    sys.stderr.write("You must specify path to database, path to folder with image data and output path\n")
    sys.exit()

# Container for icon names of images we want to dump
icons = set()
# Container for typeIDs for which we want to have renders
renders = set()

# Connect to database
conn = sqlite3.connect(os.path.expanduser(args.dump))
c = conn.cursor()

# Just get all icon IDs from dump, unwanted ones should've been filtered before
statement = "SELECT iconFile FROM icons"
c.execute(statement)
for row in c:
    value = row[0]
    if value:
        icons.add(value)
# Gather typeIDs of ships, we use renders only for them
statement = "SELECT it.typeID FROM invtypes AS it INNER JOIN invgroups AS ig ON it.groupID = ig.groupID WHERE ig.categoryID = ?"
c.execute(statement, (6,))  # 6 is ship category
for row in c:
    value = row[0]
    if value:
        renders.add(value)

# We won't need database anymore
c.close()
conn.close()

# Divide our icon file names into two categories: full name references
icons_plainnames = set()
# And references via IDs
# Format: {db name: {icon size: icon filename}}
icons_db_icodata = {}
# Helper map for previous one
icons_tuple_db = {}

for dbname in icons:
    match = re.match("^([0-9]+)_([0-9]+)$", dbname)
    if match is not None:
        # In eve, first number is used to refer DDS file
        dds = int(match.group(1))
        # As multiple icons are packed into single DDS, second number
        # is used to refer it
        num = int(match.group(2))
        # Create container for any future data
        icons_db_icodata[dbname] = {}
        # Also, fill helper map
        icons_tuple_db[(dds, num)] = dbname
    else:
        icons_plainnames.add(dbname)

# Cycle through target icons to gather some preliminary data
src_icons_path = os.path.join(os.path.expanduser(args.images), "Icons", "items")
for filename in os.listdir(src_icons_path):
    # Skip non-png files
    if filename[-4:] != ".png":
        continue
    # Also skip non-ID-named files, we don't need them here
    match = re.match("^([0-9]+)_([0-9]+)_([0-9]+)\.png$", filename)
    if match is None:
        continue
    dds = int(match.group(1))
    size = int(match.group(2))
    num = int(match.group(3))
    # Write down image size into container
    if not (dds, num) in icons_tuple_db:
        continue
    dbname = icons_tuple_db[(dds, num)]
    icons_db_icodata[dbname][size] = filename

# Create path for icon output
dst_ico_path = os.path.expanduser(args.output)
if not os.path.exists(dst_ico_path):
    os.mkdir(dst_ico_path)

# Process icons with direct names taken from the database
for iconname in icons_plainnames:
    filename = "{0}.png".format(iconname)
    src_path = os.path.join(src_icons_path, filename)
    dst_path = os.path.join(dst_ico_path, filename)
    # Define command we're going to pass to shell
    magick = "convert {0} -resize {1}x{1} png:{2}".format(src_path, ICON_SIZE, dst_path)
    os.system(magick)

# Go through all ID'ed icons we've got to find
for dbname in icons_db_icodata:
    # Check if we have our per-size dictionary filled
    icon_sizes = icons_db_icodata[dbname]
    if len(icon_sizes) == 0:
        print("Unable to find icon for {0}".format(dbname))
        continue
    dst_filename = "icon{0}.png".format(dbname)
    dst_path = os.path.join(dst_ico_path, dst_filename)
    # Just copy image if we have icon with requested size
    if ICON_SIZE in icon_sizes:
        src_filename = icon_sizes[ICON_SIZE]
        src_path = os.path.join(src_icons_path, src_filename)
        shutil.copy(src_path, dst_path)
    # Else, pick biggest image and convert it
    else:
        src_filename = icon_sizes[max(icon_sizes)]
        src_path = os.path.join(src_icons_path, src_filename)
        magick = "convert {0} -resize {1}x{1} png:{2}".format(src_path, ICON_SIZE, dst_path)
        os.system(magick)

# Create path for ship renders output
dst_render_path = os.path.join(dst_ico_path, "ships")
if not os.path.exists(dst_render_path):
    os.mkdir(dst_render_path)

# Process ship images too
src_renders_path = os.path.join(os.path.expanduser(args.images), "Renders")
for renderID in renders:
    filename = "{0}.png".format(renderID)
    src_path = os.path.join(src_renders_path, filename)
    dst_path = os.path.join(dst_render_path, filename)
    magick = "convert {0} -resize {1}x{1} png:{2}".format(src_path, RENDERS_SIZE, dst_path)
    os.system(magick)
