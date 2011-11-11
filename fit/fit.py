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

class Fit(object):
    '''
    Fit object. Each fit is built out of a number of Modules, as well as a Ship.
    This class is essentialy a container, it has no logic of its own.
    '''

    def __init__(self, ship):
        '''
        Constructor: Accepts a shipType
        '''
        self.modules = []
        self.ship = ship