##############################################################################
#       Copyright (C) 2012, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

qt_bindings = 'PyQt4'
if qt_bindings == 'PyQt4':
    # we wish to only touch sip if we're PyQt4 based (otherwise sip is unnecessary)
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

from dockers import *

__version_info__ = ['0', '1', '0']
__version__ = '.'.join(__version_info__)
