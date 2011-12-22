
# Script Constants
__script__        = "Arkanoid"
__author__        = "Frost"
__url__           = "http://passion-xbmc.org/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Arkanoid/"
__credits__       = "Team XBMC, http://xbmc.org/"
__platform__      = "xbmc media center, [ALL]"
__started__       = "26-02-2010"
__date__          = "02-04-2010"
__version__       = "pre-1.0.0"
__statut__        = "Alpha2"
__svn_revision__  = "$Revision: 715 $".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "26018"


#Modules General
import os
import sys


sys.path.append( os.path.join( os.getcwd(), "resources", "libs" ) )


if  __name__ == "__main__":
    from home import showMain
    showMain()
