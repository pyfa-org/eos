# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from importlib import import_module
from pkgutil import iter_modules


def load_submodules(path_fs, path_mod):
    """Walk through package and load all child modules within it.

    Loads just direct children, their children and anything below it should be
    loaded by packages themselves.

    Args:
        path_fs: Location of package on filesystem.
        path_mod: Location of package within running python instance.
    """
    prefix = '{}.'.format(path_mod)
    for _, name, _ in iter_modules(path_fs, prefix):
        import_module(name)
