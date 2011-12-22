
from shutil import rmtree
from traceback import print_exc
from os import getcwd, makedirs
from os.path import dirname, exists, join

from xbmcgui import Dialog
from xbmc import translatePath, getLocalizedString, Settings


CACHE = translatePath( "special://profile/script_data/Arkanoid/" )

try:
    if exists( CACHE ) and Dialog().yesno( "Arkanoid Cache", getLocalizedString( 122 ) ):
        try: rmtree( CACHE, True )
        except: print_exc()
except: print_exc()

try:
    if not exists( CACHE ): makedirs( CACHE )
except: print_exc()

try: Settings( dirname( dirname( getcwd() ) ) ).openSettings()
except:
    try: Settings( join( getcwd(), "Arkanoid" ) ).openSettings()
    except: print_exc()
