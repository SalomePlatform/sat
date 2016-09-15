# Copyright (C) 2007-2012  CEA/DEN, EDF R&D, OPEN CASCADE
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#

##
# Test functionality of :sat:{CPPCMP} module
##

# initialize salome session
import salome
salome.salome_init()

# get reference to the :sat:{CPPCMP} engine
import :sat:{CPPCMP}_ORB
comp = salome.lcc.FindOrLoadComponent('FactoryServer', ':sat:{CPPCMP}')

# test :sat:{CPPCMP} module
print "Say hello to John: should be OK"
if comp.hello(salome.myStudy, "John") != :sat:{CPPCMP}_ORB.OP_OK:
    print "ERROR: wrong operation code is returned"
else:
    print "OK"

print "Say hello to John: should answer 'already met'"
if comp.hello(salome.myStudy, "John") != :sat:{CPPCMP}_ORB.OP_ERR_ALREADY_MET:
    print "ERROR: wrong operation code is returned"
else:
    print "OK"

print "Say goodbye to Margaret: should answer 'did not meet yet'"
if comp.goodbye(salome.myStudy, "Margaret") != :sat:{CPPCMP}_ORB.OP_ERR_DID_NOT_MEET:
    print "ERROR: wrong operation code is returned"
else:
    print "OK"

print "Say hello to John: should be OK"
if comp.goodbye(salome.myStudy, "John") != :sat:{CPPCMP}_ORB.OP_OK:
    print "ERROR: wrong operation code is returned"
else:
    print "OK"

print "Say hello to John: should answer 'did not meet yet'"
if comp.goodbye(salome.myStudy, "John") != :sat:{CPPCMP}_ORB.OP_ERR_DID_NOT_MEET:
    print "ERROR: wrong operation code is returned"
else:
    print "OK"
