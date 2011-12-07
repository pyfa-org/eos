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

import codecs
import os.path
import re
import sqlite3

import const

class Dumper(object):
    """
    Handle dumping of data to storage
    """
    def __init__(self, tables):
        self.tables = tables

    def sqlite(self, path):
        """Dump everything we've got into SQLite file"""
        # Check if dump file already exists and remove it
        if os.path.exists(path):
            os.remove(path)

        # Connect to SQLite dump database
        conn = sqlite3.connect(path)
        c = conn.cursor()

        # Data type specification for SQLite
        datatypes = {const.type_BOOL: "INTEGER",
                     const.type_INT: "INTEGER",
                     const.type_FLOAT: "REAL",
                     const.type_STR: "TEXT"}

        # For each table
        for tablename in sorted(self.tables):
            table = self.tables[tablename]
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

    def mysql(self, path):
        """Dump everything we've got into MySQL statements file"""
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
        for tablename in sorted(self.tables):
            table = self.tables[tablename]
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
                if column.datatype == const.type_BOOL:
                    colspec.append("TINYINT")
                # Integers are a bit more complex
                elif column.datatype == const.type_INT:
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
                elif column.datatype == const.type_FLOAT:
                    colspec.append("DOUBLE")
                # String is also complex
                elif column.datatype == const.type_STR:
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
