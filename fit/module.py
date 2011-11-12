'''
Created on 11-nov.-2011

@author: cncfanatics

This file is part of eos.

eos is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Eos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with eos.  If not, see <http://www.gnu.org/licenses/>.
'''

class Module(object):
    '''
    Module class. This class is a fit-specific wrapper around a Type. It keeps track of all the fit-specific information of it.
    As this class is fit specific, the same module shouldn't be added onto more then one fit at the same time.
    '''

    def __init__(self, type):
        '''
        Constructor. Accepts a Type
        '''
        self.type = type

    def run(self):
        pass

    def undo(self):
        pass