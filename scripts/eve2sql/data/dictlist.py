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

class DictList(object):
    """
    Provides merged functionality of dictionary and and list
    """
    def __init__(self):
        self.__childlist = []
        self.__childnamemap = {}

    def __getitem__(self, name):
        return self.__childnamemap.__getitem__(name)

    def get(self, name, default=None):
        return self.__childnamemap.get(name, default)

    def __len__(self):
        return self.__childlist.__len__()

    def __iter__(self):
        return self.__childlist.__iter__()

    def __next__(self):
        return self.__childlist.__next__()

    def append(self, child):
        if not child.name in self.__childnamemap:
            self.__childlist.append(child)
            self.__childnamemap[child.name] = child
        else:
            raise ValueError("child with this name already exists")

    def remove(self, child):
        if child.name in self.__childnamemap:
            self.__childlist.remove(child)
            del self.__childnamemap[child.name]
        else:
            raise ValueError("no such child")

    def index(self, child):
        return self.__childlist.index(child)
