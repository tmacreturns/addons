"""
    by frost (passion-xbmc.org)
"""

#Modules General
import os
from traceback import print_exc
from marshal import dumps, loads

#Modules XBMC
import xbmc
import xbmcgui


CWD = os.getcwd().rstrip( ";" )
BASE_RESOURCE_PATH = os.path.join( CWD, "resources" )

SCORES_PATH = xbmc.translatePath( "special://profile/script_data/Arkanoid/scores.doh" )
if not os.path.isdir( os.path.dirname( SCORES_PATH ) ): os.makedirs( os.path.dirname( SCORES_PATH ) )



DEBUG = 0
class customDict( dict ):
    """ customized dict, don't raise KeyError exception, return None instead """
    def __getitem__( self, key ):
        if self.has_key( key ):
            return dict.__getitem__( self, key )
        elif DEBUG:
            print "WallsDict::getitem::Error: Wall %s not exists" % str( key )
        return None

    def __delitem__( self, key ):
        if self.has_key( key ):
            dict.__delitem__( self, key )
        elif DEBUG:
            print "WallsDict::delitem::Error: Wall %s not exists" % str( key )


def getUserSkin():
    default_skin = "Classic"
    try:
        skin_setting = xbmc.Settings( CWD ).getSetting( "skin" )
        if skin_setting != default_skin and not os.path.exists( os.path.join( CWD, "resources", "skins", skin_setting ) ):
            skin_setting = None
    except:
        skin_setting = None
        print_exc()
    if not skin_setting: current_skin = xbmc.getSkinDir()
    else: current_skin = skin_setting
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = default_skin
    return current_skin, not force_fallback


CURRENT_SKIN, FORCE_FALLBACK = getUserSkin()
MEDIAS_PATH = os.path.join( BASE_RESOURCE_PATH, "skins", CURRENT_SKIN, "media" )
SOUNDS_PATH = os.path.join( BASE_RESOURCE_PATH, "skins", CURRENT_SKIN, "sounds" )


def setSortedScores( iterable ):
    try:
        # set level sort by ascending 
        L = sorted( iterable, key=lambda x: x[ 1 ] )
        # set name sort by ascending 
        N = sorted( L, key=lambda x: x[ 2 ] )
        # finally set score sort by descending
        iterable = sorted( N, key=lambda x: x[ 0 ], reverse=True )
    except:
        print_exc()
    return iterable


def loadScores():
    scores = {}
    try:
        # load score
        f = open( SCORES_PATH, "rb" )
        scores = loads( eval( f.read() ) )
        f.close()
    except IOError:
        pass
    except:
        print_exc()
    return scores #setSortedScores( scores )


def saveScores( dico ):
    try:
        # save scores
        f = open( SCORES_PATH, "wb" )
        f.write( repr( dumps( dico ) ) )
        f.close()
        return True
    except IOError:
        pass
    except:
        print_exc()


def SFX( sound, muted=False ):
    if not muted:
        xbmc.playSFX( os.path.join( SOUNDS_PATH, sound ) )


def splitLevel( iterable, start=0, step=13, end=0 ):
    """Return a list containing an slice of iterable.
    start (!) defaults to 0.; step is split index, (!) defaults to 13.; end (!) defaults to 0.
    For example, splitLevel(range(4)) returns [[0, 1, 2, 3]].
    """
    try:
        splited = []
        if end <= 0:
            end = len( iterable )
 
        for index in xrange( step, end, step ):
            splited.append( iterable[ start:index ] )
            start = index
        splited.append( iterable[ start:end ] )
 
        return splited
    except:
        print_exc()
 
    return [ iterable ]


def getBrowseDialog( default="", heading="", dlg_type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value









