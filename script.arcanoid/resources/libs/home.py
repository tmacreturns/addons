"""
    by frost (passion-xbmc.org)
"""

#Modules General
import os
import time
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui

#Modules Customs
import game
import utilities
from geometry import Rect


CWD = os.getcwd().rstrip( ";" )

MEDIAS_PATH = utilities.MEDIAS_PATH
BASE_RESOURCE_PATH = utilities.BASE_RESOURCE_PATH
CURRENT_SKIN, FORCE_FALLBACK = utilities.CURRENT_SKIN, utilities.FORCE_FALLBACK


class Main( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )

    def onInit( self ):
        self.GAME = None
        self.set_constants()
        self.setSettings()
        self.setHome()

    def setSettings( self ):
        SETTINGS = { "custom_bg": "", "bg_ingame": 0, "custom_bg_ingame": "", "mouse_zone": False }
        try:
            settings = xbmc.Settings( CWD )
            SETTINGS[ "custom_bg" ] = settings.getSetting( "custom_bg" )
            SETTINGS[ "bg_ingame" ] = int( settings.getSetting( "bg_ingame" ) )
            SETTINGS[ "custom_bg_ingame" ] = settings.getSetting( "custom_bg_ingame" )
            SETTINGS[ "mouse_zone" ] = ( settings.getSetting( "mouse_zone" ) == "true" )
        except:
            print_exc()
        self.setProperty( "custom_bg", ( "", SETTINGS[ "custom_bg" ] )[ os.path.exists( SETTINGS[ "custom_bg" ] ) ] )
        cbg_exists = os.path.exists( SETTINGS[ "custom_bg_ingame" ] )
        self.setProperty( "bg_ingame", ( "0",  str( SETTINGS[ "bg_ingame" ] ) )[ cbg_exists ] )
        self.setProperty( "custom_bg_ingame", ( "", SETTINGS[ "custom_bg_ingame" ] )[ cbg_exists ] )
        self.setProperty( "mouse_zone", ( "", "true" )[ SETTINGS[ "mouse_zone" ] ] )

    def setHome( self ):
        self.labelGetReady.setVisible( False )
        self.panelControls.setVisible( True )
        self.setFocusId( 9000 )
        self.setProperty( "score.highscore", self.getHighScores()[ 0 ] )
        self.setProperty( "score.player", "" )
        self.setProperty( "level.level", "" )
        self.setProperty( "Intro", "" )
        self.setProperty( "GameOver", "" )

    def getHighScores( self ):
        defaultScores = [ ( "50000", "5", "AAA", "doh/01.png" ), ( "45000", "4", "BBB", "doh/01.png" ),
            ( "40000", "3", "CCC", "doh/01.png" ), ( "35000", "2", "DDD", "doh/01.png" ), ( "30000", "1", "EEE", "doh/01.png" ) ]

        scores = utilities.loadScores()
        # ...1 = classic mode
        try: l1 = scores[ "local1" ]
        except: l1 = defaultScores
        try: o1 = scores[ "online1" ]
        except: o1 = defaultScores
        try: high1 = utilities.setSortedScores( l1+o1 )[ 0 ][ 0 ]
        except: high1 = "50000"
        # ...2 = tournament mode
        try: l2 = scores[ "local2" ]
        except: l2 = defaultScores
        try: o2 = scores[ "online2" ]
        except: o2 = defaultScores
        try: high2 = utilities.setSortedScores( l2+o2 )[ 0 ][ 0 ]
        except: high2 = "50000"

        return high1, high2

    def set_constants( self ):
        self.screenGamePlay = Rect( self.getControl( 1000 ).getPosition()[ 0 ], self.getControl( 1000 ).getPosition()[ 1 ],
            self.getControl( 1000 ).getWidth(), self.getControl( 1000 ).getHeight() )

        self.defaultWallRect = Rect( self.screenGamePlay.left, self.screenGamePlay.top,
            self.getControl( 100 ).getWidth(), self.getControl( 100 ).getHeight() )

        self.defaultVausRect = Rect( self.getControl( 110 ).getPosition()[ 0 ], self.getControl( 110 ).getPosition()[ 1 ],
            self.getControl( 110 ).getWidth(), self.getControl( 110 ).getHeight() )

        self.defaultVausBigRect = Rect( self.getControl( 109 ).getPosition()[ 0 ], self.getControl( 109 ).getPosition()[ 1 ],
            self.getControl( 109 ).getWidth(), self.getControl( 109 ).getHeight() )

        self.ballControl = self.getControl( 111 )
        # self.defaultBallRect.left = offset of self.defaultVausRect.left
        self.defaultBallRect = Rect( self.ballControl.getPosition()[ 0 ] - self.defaultVausRect.left,
            self.ballControl.getPosition()[ 1 ], self.ballControl.getWidth(), self.ballControl.getHeight() )

        self.defaultFireRect = Rect( self.getControl( 112 ).getPosition()[ 0 ], self.getControl( 112 ).getPosition()[ 1 ],
            self.getControl( 112 ).getWidth(), self.getControl( 112 ).getHeight() )

        self.defaultEnemyRect1 = Rect( self.getControl( 106 ).getPosition()[ 0 ], self.getControl( 106 ).getPosition()[ 1 ],
            self.getControl( 106 ).getWidth(), self.getControl( 106 ).getHeight() )

        self.defaultEnemyRect2 = Rect( self.getControl( 107 ).getPosition()[ 0 ], self.getControl( 107 ).getPosition()[ 1 ],
            self.getControl( 107 ).getWidth(), self.getControl( 107 ).getHeight() )

        # next level bonus
        self.wrapEscape = self.getControl( 103 )
        self.wrapEscape.setVisible( False )

        self.labelGetReady = self.getControl( 1001 )
        self.labelGetReady.setVisible( False )

        self.wallsContainer = self.getControl( 250 )
        self.vausPlayersContainer = self.getControl( 150 )
        self.vausControl = self.getControl( 500 )

        self.panelControls = self.getControl( 10000 )

    def onFocus( self, controlID ):
        pass

    def launchGame( self, level=0, mode=0, customlevel=None ):
        #mode: 1=normal, 2=tournament, 3=custom level, 4=practice
        # on lance la class Game avec la self de cette class
        if not self.GAME:
            self.GAME = game.Game( self, level, mode, customlevel=customlevel )

    def launchFire( self ):
        # max shots = 1, not allow rapidfire :))
        if self.GAME:
            self.GAME.fireShots += 1

    def onClick( self, controlID ):
        try:
            if self.GAME and self.GAME.GameOver:
                del self.GAME
                self.GAME = None

            if self.GAME and controlID == 500:
                if not self.GAME.threadLevel and not self.GAME.ballRunning:
                    self.GAME.startLevel()
                elif self.GAME.vaus_statut == "LASER":
                    #else:
                    self.launchFire()

            elif not self.GAME and controlID == 201:
                mode = ( controlID - 200 )
                self.launchGame( 0, mode )

            elif not self.GAME and controlID == 202:
                mode = ( controlID - 200 )
                self.launchGame( 0, mode )

            elif not self.GAME and controlID == 203:
                mode = ( controlID - 200 )
                #browse custom stage
                stg = utilities.getBrowseDialog( os.path.join( BASE_RESOURCE_PATH, "custom_levels" )+os.sep,
                    heading="Select Your Stage", mask=".stage" )
                if stg and os.path.isfile( stg ):
                    f = open( stg, "r" )
                    bg, stage = eval( f.read() )
                    f.close()
                    #test valide stage and background
                    error_info = "Bad file! %s" % stg
                    if not len( stage ) == 260: raise error_info
                    for colrow in stage:
                        if not ( 0 <= colrow <= 10 ): raise error_info
                    if os.path.exists( bg ): bg = bg
                    elif bg and not os.path.exists( bg ): bg = os.path.join( MEDIAS_PATH, bg )
                    stageName = os.path.splitext( os.path.basename( stg ) )[ 0 ]
                    customlevel = bg, stage, stageName
                    self.launchGame( 0, mode, customlevel )

            elif not self.GAME and controlID == 204:
                mode = ( controlID - 200 )
                stage_path = utilities.getBrowseDialog( os.path.join( BASE_RESOURCE_PATH, "media", "stages" )+os.sep,
                    heading="Select Practice Stage", dlg_type=2, shares="pictures", use_thumbs=True )
                level_id = os.path.splitext( os.path.basename( stage_path ) )[ 0 ].split( "_" )[ -1 ]
                if level_id.isdigit():
                    mode = ( mode, 5 )[ "tournament" in os.path.basename( stage_path ).lower() ]
                    self.launchGame( int( level_id ), mode )

            elif controlID == 122:
                import editor
                w = editor.levelEditor( "levelEditor.xml", CWD, CURRENT_SKIN, FORCE_FALLBACK )
                w.doModal()
                del w, editor

            elif controlID == 125:
                w = HighScores( "highScores.xml", CWD, CURRENT_SKIN, FORCE_FALLBACK )
                w.doModal()
                del w

            elif controlID == 320:
                self.closeGame()

            elif controlID == 123:
                self._stop_game()

            elif controlID == 126:
                settings = xbmc.Settings( CWD )
                skin_setting = settings.getSetting( "skin" )
                settings.openSettings()
                xbmc.sleep( 500 )
                self.setSettings()
                if skin_setting != xbmc.Settings( CWD ).getSetting( "skin" ):
                    self.closeGame()
                    xbmc.executescript( os.path.join( CWD, 'default.py' ) )

            elif controlID == 127:
                import infos
                w = infos.Info( "infos.xml", CWD, CURRENT_SKIN, FORCE_FALLBACK )
                w.doModal()
                del w, infos
        except:
            print_exc()

    def add_score( self, mode, score, level ):
        HS = HighScores( "highScores.xml", CWD, CURRENT_SKIN, FORCE_FALLBACK )
        if HS.addScore( mode, score, level ):
            HS.doModal()
        del HS

    def onAction( self, action ):
        if action in ( 9, 10 ):
            self.closeGame()
        elif self.GAME and action == 117:
            self.GAME.pause()

    def closeGame( self ):
        self._stop_game()
        self.close()

    def _stop_game( self ):
        if self.GAME:
            try: self.GAME.stopGame()
            except: pass
        del self.GAME
        self.GAME = None
        self.setHome()


class HighScores( xbmcgui.WindowXMLDialog ):
    title1 = "THE FOLLOWING ARE[CR]THE RECORDS OF THE BRAVEST[CR]FIGHTERS OF ARKANOID"
    title2 = "THE FOLLOWING ARE[CR]THE RECORDS OF THE BRAVEST[CR]FIGHTERS OF TOURNEMANT ARKANOID"

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )

        self.scores = self.getScores()

    def getScores( self ):
        defaultScores = [ ( "50000", "5", "AAA", "doh/01.png" ), ( "45000", "4", "BBB", "doh/01.png" ),
            ( "40000", "3", "CCC", "doh/01.png" ), ( "35000", "2", "DDD", "doh/01.png" ), ( "30000", "1", "EEE", "doh/01.png" ) ]

        scores = utilities.loadScores()
        # ...1 = classic mode
        try: l1 = utilities.setSortedScores( scores[ "local1" ] )
        except: l1 = utilities.setSortedScores( defaultScores )
        try: o1 = utilities.setSortedScores( scores[ "online1" ] )
        except: o1 = utilities.setSortedScores( defaultScores )
        
        # ...2 = tournament mode
        try: l2 = utilities.setSortedScores( scores[ "local2" ] )
        except: l2 = utilities.setSortedScores( defaultScores )
        try: o2 = utilities.setSortedScores( scores[ "online2" ] )
        except: o2 = utilities.setSortedScores( defaultScores )

        return { "local1": l1, "local2": l2, "online1": o1, "online2": o2 }

    def addScore( self, mode, score, level ):
        addto = []
        if mode == 1:
            Llow = self.scores[ "local1" ][ -1 ][ 0 ]
            Olow = self.scores[ "online1" ][ -1 ][ 0 ]
            if score >= int( Llow ): addto.append( "local1" )
            if score >= int( Olow ): addto.append( "online1" )
        elif mode == 2:
            Llow = self.scores[ "local2" ][ -1 ][ 0 ]
            Olow = self.scores[ "online2" ][ -1 ][ 0 ]
            if score >= int( Llow ): addto.append( "local2" )
            if score >= int( Olow ): addto.append( "online2" )
        added = False
        if addto:
            # enter name
            kb = xbmc.Keyboard( "", "Enter your name" )
            kb.doModal()
            if kb.isConfirmed():
                name = kb.getText()
                if bool( name ):
                    added = True
                    add = ( str( score ), str( level ), name, "doh/01.png" )
                    for key in addto:
                        self.scores[ key ].append( add )
                    #save
                    added = utilities.saveScores( self.scores )
        return added

    def onInit( self ):
        self.getControl( 10 ).setEnabled( 0 )
        self.setProperty( "recordtext", self.title1 )
        self.setContainer( self.scores[ "local1" ] )

    def setContainer( self, scores ):
        try:
            self.getControl( 49 ).reset()
            showScores = utilities.setSortedScores( scores )[ :5 ]
            POS = [ "1ST", "2RD", "3ND", "4TH", "5TH" ]
            for count, value in enumerate( showScores ):
                score, round, name, icon = value
                listitem = xbmcgui.ListItem( POS[ count ], "", icon, icon )
                listitem.setProperty( "player.score", score )
                listitem.setProperty( "player.round", round )
                listitem.setProperty( "player.name", name )
                self.getControl( 49 ).addItem( listitem )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            self.getControl( 10 ).setEnabled( ( controlID in [ 6, 8, 10 ] ) )
            if controlID == 5: #local1
                self.setProperty( "recordtext", self.title1 )
                self.setContainer( self.scores[ "local1" ] )

            elif controlID == 6: # online1
                self.setProperty( "recordtext", self.title1 )
                self.setContainer( self.scores[ "online1" ] )

            elif controlID == 7: #local2
                self.setProperty( "recordtext", self.title2 )
                self.setContainer( self.scores[ "local2" ] )

            elif controlID == 8: # online2
                self.setProperty( "recordtext", self.title2 )
                self.setContainer( self.scores[ "online2" ] )

            elif controlID == 10: # refresh online 1 and 2 same time
                pass

        except:
            print_exc()

    def onAction( self, action ):
        if action in ( 9, 10 ):
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .4 )
        self.close()


def showMain():
    #xbmc.enableNavSounds( 0 )
    w = None
    try:
        w = Main( "arkanoid.xml", CWD, CURRENT_SKIN, FORCE_FALLBACK )
    except Exception, e:
        print_exc()
        #TypeError
        if CURRENT_SKIN == "Classic":
            # fatal error popup user for contact me
            xbmcgui.Dialog().ok( "Fatal Error!!!", "Contact Frost to passion-xbmc.org" )
            raise "Fatal Error: contact Frost to passion-xbmc.org"
        if str( e ) == "XML File for Window is missing":
            #reset skin setting and reload script
            xbmcgui.Dialog().ok( "Error!!!", "XML File for Window is missing in Skin: %s" % CURRENT_SKIN, "", "Default skin will be loaded..." )
            print "Error on load xml in skin: %s" % CURRENT_SKIN
            xbmc.Settings( CWD ).setSetting( "skin", "Classic" )
            xbmc.executescript( os.path.join( CWD, 'default.py' ) )
    if w:
        w.doModal()
        del w
    #xbmc.enableNavSounds( 1 )
