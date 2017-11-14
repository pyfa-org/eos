# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


"""
Find all constants defined in eos.const package, which are not used in eos'
and tests' code.
"""


import ast
import os


class EnumSeeker(ast.NodeVisitor):

    def __init__(self, enum_data):
        self.enum_data = enum_data

    def visit_ClassDef(self, enum_class_node):
        # Check only enums inherited from IntEnum class
        if (
            len(enum_class_node.bases) != 1 or
            not isinstance(enum_class_node.bases[0], ast.Name) or
            enum_class_node.bases[0].id != 'IntEnum'
        ):
            return
        for enum_assignment_node in enum_class_node.body:
            # Only assignments to name are recorded
            if not isinstance(enum_assignment_node, ast.Assign):
                continue
            for enum_item_name_node in enum_assignment_node.targets:
                if not isinstance(enum_item_name_node, ast.Name):
                    continue
                # Get data about enum entries into container
                item_names = self.enum_data.setdefault(
                    enum_class_node.name, set())
                item_names.add(enum_item_name_node.id)


class ReferenceSeeker(ast.NodeVisitor):

    def __init__(self, enum_data, used_enums):
        self.enum_data = enum_data
        self.used_enums = used_enums
        # Format: {local enum name: original enum name}
        self.alt_names = {}

    def visit_Import(self, node):
        self.__find_alt_name(node)

    def visit_ImportFrom(self, node):
        self.__find_alt_name(node)

    def __find_alt_name(self, node):
        for alias in node.names:
            if alias.asname is None:
                continue
            if alias.name not in self.enum_data:
                continue
            self.alt_names[alias.asname] = alias.name

    def visit_Attribute(self, node):
        # Get enum name
        rightmost = self.__get_rightmost_value(node.value)
        if rightmost in self.alt_names:
            enum_name = self.alt_names[rightmost]
        elif rightmost in self.enum_data:
            enum_name = rightmost
        else:
            return
        # Get attribute name
        attr_name = node.attr
        # If it's in enum, make sure it's marked as used
        if attr_name in self.enum_data[enum_name]:
            used_attrs = self.used_enums.setdefault(enum_name, set())
            used_attrs.add(attr_name)

    def __get_rightmost_value(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.__get_rightmost_value(node.value)
        # We're not interested in any constructs besides obj1.obj2.attribute,
        # which are composed of Attribute and Name nodes, thus we're not
        # handling any other node types
        else:
            return None


def get_enum_data(path):
    """Return data about fields used in const enums as map."""
    # Format: {enum name: {enum item names}}
    enum_data = {}
    for ast_root in _get_asts_in_dir(path):
        EnumSeeker(enum_data).visit(ast_root)
    return enum_data


def get_used_enums(path, enum_data):
    """Find out which fields from passed enums are used."""
    # Format: {enum name: {enum item names}}
    used_enums = {}
    for ast_root in _get_asts_in_dir(path):
        ReferenceSeeker(enum_data, used_enums).visit(ast_root)
    return used_enums


def _get_asts_in_dir(path):
    """Iterate through all source files' ASTs."""
    for dir_path, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] != '.py':
                continue
            with open(os.path.join(dir_path, file)) as f:
                data = f.read()
            try:
                ast_root = ast.parse(data)
            except KeyboardInterrupt:
                raise
            except:
                print('failed to parse source for {}'.format(
                    os.path.join(dir_path, file)))
            else:
                yield ast_root


def print_results(enum_data, header):
    if enum_data:
        print('{}:'.format(header))
        for enum_name in sorted(enum_data):
            print('  {}'.format(enum_name))
            for attr_name in sorted(enum_data[enum_name]):
                print('    {}'.format(attr_name))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))

    enum_data = get_enum_data(os.path.join(root_dir, 'eos', 'const'))
    used_by_eos = get_used_enums(os.path.join(root_dir, 'eos'), enum_data)
    used_by_tests = get_used_enums(os.path.join(root_dir, 'tests'), enum_data)

    # Format: {enum name: {enum item names}}
    unused = {}
    only_tests = {}

    for enum_name, enum_attrs in enum_data.items():
        for enum_attr in enum_attrs:
            # Used by eos
            if enum_attr in used_by_eos.get(enum_name, ()):
                continue
            # Not used by eos, but used by tests
            if enum_attr in used_by_tests.get(enum_name, ()):
                only_test_attrs = only_tests.setdefault(enum_name, set())
                only_test_attrs.add(enum_attr)
                continue
            # Not used at all
            unused_attrs = unused.setdefault(enum_name, set())
            unused_attrs.add(enum_attr)

    print_results(unused, 'Enum entries which are not used at all')
    print_results(only_tests, 'Enum entries which are used only in tests')


if __name__ == '__main__':
    main()
