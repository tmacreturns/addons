"""
    by frost (passion-xbmc.org)
"""

#Modules General
import threading
from operator import neg
from time import sleep, time
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui

#Modules Customs
import utilities
from sprites import *


CWD = os.getcwd().rstrip( ";" )

SFX = utilities.SFX
MEDIAS_PATH = utilities.MEDIAS_PATH
CURRENT_SKIN, FORCE_FALLBACK = utilities.CURRENT_SKIN, utilities.FORCE_FALLBACK


class Game:
    def __init__( self, window, level=0, mode=1, customlevel=None ):
        self.window = window
        self._level = level
        self.mode   = mode
        self.customlevel = customlevel
        self.threadLevel   = None
        self.threadEnemies = None
        self.GameOver = False
        self.paused = False

        # In Main::set_constants( self )
        self.defaultWallRect      = self.window.defaultWallRect
        self.defaultVausRect      = self.window.defaultVausRect
        self.defaultVausBigRect   = self.window.defaultVausBigRect
        self.wallsContainer       = self.window.wallsContainer
        self.panelControls        = self.window.panelControls
        self.wrapEscape           = self.window.wrapEscape
        self.labelGetReady        = self.window.labelGetReady
        self.vausControl          = self.window.vausControl
        self.vausPlayersContainer = self.window.vausPlayersContainer

        # set constants and level
        self.resets()
        if not self._level and not self.customlevel:
            self.intro()
        self.set_level( self._level or 1 )

    def pause( self ):
        self.paused = not self.paused
        self.window.getControl( 121 ).setEnabled( not self.paused )
        self.window.getControl( 122 ).setEnabled( not self.paused )
        self.window.setProperty( "game.paused", ( "", "true" )[ self.paused ] )
        self.panelControls.setVisible( self.paused )
        self.window.setFocusId( ( 500, 9000 )[ self.paused ] )

    def resets( self ):
        self.set_default_game_values()
        self.remove_walls()
        self.window.clearList()
        self.vausControl.reset()
        self.vausPlayersContainer.reset()

    def remove_walls( self ):
        try:
            self.wallsControls = utilities.customDict()
            self.wallsContainer.reset()
        except:
            print_exc()

    def intro( self ):
        try:
            self.gameStarted = True
            self.window.setFocusId( 500 )
            self.panelControls.setVisible( False )
            SFX( "Intro.wav" )
            intro = 'THE ERA AND TIME OF\nTHIS STORY IS UNKNOWN.\n\nAFTER THE MOTHERSHIP\n"ARKANOID" WAS DESTROYED,\nA SPACECRAFT "VAUS"\nSCRAMBLED AWAY FROM IT.\n\nBUT ONLY TO BE\nTRAPPED IN SPACE WARPED\nBY SOMEONE........'
            letters = ""
            for letter in intro:
                if not self.gameStarted: break
                letters += letter
                self.window.setProperty( "Intro", letters )
                xbmc.sleep( 10 )
            xbmc.sleep( 500 )
            self.window.setProperty( "Intro", "" )
        except:
            print_exc()

    def set_default_game_values( self ):
        self.gameStarted   = False
        self.ballRunning   = False
        self.wallsControls = utilities.customDict()
        self.totalWalls    = 0
        self.highscore     = int( self.window.getHighScores()[ ( 0, 1 )[ ( self.mode in [ 2, 5 ] ) ] ] )#50000
        self.player_score  = 0
        self.fireShots     = 0
        self.current_level = 0
        self.vausPlayers   = 3
        self.ballSpeed     = 6
        self.vaus_statut   = "NORMAL"
        self.vausHasCatch  = False

        self.window.clearProperties()
        # set default container.properties
        self.window.setProperty( "Intro", "" )
        # bonus property
        self.window.setProperty( "bonus.enlarge", "" )
        self.window.setProperty( "vaus.statut", "NORMAL" )
        #level property
        self.window.setProperty( "level.background", "" )
        self.window.setProperty( "level.level", str( self.current_level ) )
        self.window.setProperty( "level.ballRunning", "" )
        # score property
        self.window.setProperty( "score.highscore", str( self.highscore ) )
        self.window.setProperty( "score.player", str( self.player_score ) )

    def set_level( self, level_id=1 ):
        try:
            self.wrapEscape.setVisible( False )
            self.labelGetReady.setVisible( False )
            self.panelControls.setVisible( False )

            self.remove_walls()
            self.window.clearList()
            self.vausControl.reset()

            SFX( "ready.wav" )

            #mode: 1=normal, 2=tournament, 3=custom level, 4=practice normal, 5=practice tournament
            if self.mode == 1:
                self.current_level = level_id
                level = arkanoid.Levels()[ level_id ]
            elif self.mode == 2:
                self.current_level = level_id
                level = arkanoid.TournamentLevels()[ level_id ]
            elif self.mode == 3:
                #while and load level
                #customlevel = bg, stage, stageName
                self.current_level = self._level
                level = self.customlevel[ 1 ]
                pass
            elif self.mode == 4:
                #while level
                self.current_level = self._level
                level = arkanoid.Levels()[ self._level ]
            elif self.mode == 5:
                #while level 
                self.current_level = self._level
                level = arkanoid.TournamentLevels()[ self._level ]

            if not self.customlevel:
                self.window.setProperty( "level.level", str( self.current_level ) )
                count = arkanoid.getLevelBackground( level_id )
                self.window.setProperty( "level.background", "BG_big%s.png" % str( count ) )
            else:
                self.window.setProperty( "level.level", self.customlevel[ 2 ] )
                self.window.setProperty( "level.background", self.customlevel[ 0 ] )

            self.window.setProperty( "score.highscore", str( self.highscore ) )
            self.window.setProperty( "score.player", str( self.player_score ) )

            splited = utilities.splitLevel( level )
            splited.reverse()
            # remove last line if is empty
            for c, l in enumerate( splited ):
                if sum( l ): break
            splited = splited[ c: ]
            splited.reverse()

            count = 0
            self.totalWalls = 0 # nombre de brick à détruire
            x, y, w, h = self.defaultWallRect.x, self.defaultWallRect.y, self.defaultWallRect.w, self.defaultWallRect.h

            constants_level = [ self.current_level, self.mode, self.customlevel ]
            walls_items = []
            for line, rows in enumerate( splited ):
                posy = y + h * line
                for row, img_id in enumerate( rows ):
                    posx = x + w * row
                    wall_item = xbmcgui.ListItem()
                    if img_id:
                        
                        wall = Wall( posx, posy, w, h, img_id, constants_level, count )
                        wall_item.setIconImage( os.path.join( MEDIAS_PATH, wall.image ) )
                        self.wallsControls[ count ] = wall
                        if img_id < 10:
                            self.totalWalls += 1
                    count += 1
                    #self.wallsContainer.addItem( wall_item )
                    walls_items.append( wall_item )
                    #time.sleep( .01 )
            self.wallsContainer.addItems( walls_items )
            self.addVausPlayers()
        except:
            print_exc()

    def addVausControl( self ):
        self.vaus_statut = "NORMAL"
        self.window.setProperty( "vaus.statut", "NORMAL" )
        self.labelGetReady.setVisible( True )
        self.vausControl.reset()
        size = ( 26, 24 )[ 0 ] #0 = normal vaus; 1 = big vaus
        self.vausControl.addItems( [ xbmcgui.ListItem() ] * size )
        self.vausControl.selectItem( int( size/2 ) )
        self.window.setFocusId( 500 )

    def addVausPlayers( self ):
        try:
            self.ballRunning = False
            self.window.setProperty( "level.ballRunning", "" )
            self.vausControl.reset()
            self.vausPlayersContainer.reset()
            if self.vausPlayers > 0:
                self.vausPlayers -= 1
                if self.vausPlayers > 0:
                    self.vausPlayersContainer.addItems( [ xbmcgui.ListItem() ] * self.vausPlayers )
                self.addVausControl()
                if self.gameStarted:
                    SFX( "ready.wav" )
                    sleep( 3 )
            else:
                self.endGame()
        except:
            print_exc()

    def setCollideWall( self, key, ping=0 ):
        try:
            wall = self.wallsControls[ key ]
            if wall is not None:
                # add animated wall for type 0 or 2
                if ping:
                    SFX( "ping2.wav" )
                if wall.shots_destroy == 1:
                    # set scrore
                    self.player_score += ( wall.score * ( 1, self.current_level )[ wall.type == 5 ] )
                    self.window.setProperty( "score.player", str( self.player_score ) )
                    if self.player_score > self.highscore:
                        self.highscore = self.player_score
                        self.window.setProperty( "score.highscore", str( self.highscore ) )

                    #now remove wall
                    self.wallsContainer.getListItem( key ).setIconImage( wall.image.replace( ".png", ".gif" ) )
                    #if wall.type != 5:
                    #    arkanoid.CapsulesBonus().setCapsule( self, wall, self.current_level )
                    del self.wallsControls[ key ]
                    self.totalWalls -= 1
                if wall.shots_destroy >= 2:
                    wall.shots_destroy -= 1
                    #if wall.shots_destroy == 1:
                    #    self.wallsContainer.getListItem( key ).setIconImage( os.path.join( MEDIAS_PATH, wallsValues()[ 7 ][ 0 ] ) )
                return True
        except:
            print_exc()

    def getCurrentVausRect( self ):
        try:
            # vaus step = 24
            xbmcgui.lock()
            vaus_pos = self.vausControl.getSelectedPosition()
            offset = vaus_pos * 24
            if self.vaus_statut != "BIG":
                # normal vaus
                vaus_width = self.defaultVausRect.w
            else:
                # big vaus
                vaus_width = self.defaultVausBigRect.w
            default_offset = int( ( vaus_width - 24 ) / 2 ) #-36
            offset -= default_offset
            if vaus_pos == 0:    offset += default_offset
            elif vaus_pos == 25: offset -= default_offset

            if self.vaus_statut != "BIG":
                # normal vaus
                if vaus_pos == 1:  offset += ( default_offset / 2 )
                elif vaus_pos == 24: offset -= ( default_offset / 2 )
            else:
                # big vaus
                if vaus_pos == 1:  offset += ( ( default_offset / 3 ) * 2 )
                elif vaus_pos == 2: offset += ( default_offset / 3 )
                elif vaus_pos == 23:  offset -= ( default_offset / 3 )
                elif vaus_pos == 24: offset -= ( ( default_offset / 3 ) * 2 )

            xbmcgui.unlock()
            return Rect( self.defaultWallRect.left+offset, self.defaultVausRect.top, vaus_width, self.defaultVausRect.h )
        except:
            print_exc()
        xbmcgui.unlock()
        return Rect( 0, 0, 0, 0 )

    def startLevel( self ):
        self.labelGetReady.setVisible( False )
        self.window.setProperty( "level.ballRunning", "true" )
        self.ballRunning = True
        self.gameStarted = True
        self.GameOver = False

        self.commonLock = threading.Lock()
        if not self.threadLevel or not self.ballRunning:
            self.threadLevel = onLevel( self, self.commonLock )
            self.threadLevel.setDaemon( True )
            self.threadLevel.start()

    def endGame( self ):
        if self.paused: self.pause()
        self.window.setProperty( "GameOver", "Game Over" )
        SFX( "gameover.wav" )
        sleep( 3 )
        self.window.setProperty( "GameOver", "" )
        #on verifie si le score doit etre inscrie
        self.window.add_score( self.mode, self.player_score, self.current_level )
        self.resets()
        self.window.setHome()
        self.GameOver = True
        print "Thread-Game: Game Over"

    def stopGame( self ):
        self.gameStarted = False
        if self.paused: self.pause()
        #SFX( "gameover.wav" )
        try:
            self.threadLevel.stop()
            while self.threadLevel.isAlive():
                sleep( 0.02 )
        except: pass

        self.resets()
        self.window.setHome()
        self.GameOver = True
        print "Thread-Game: Stopped"

    def levelUp( self ):
        self.window.setProperty( "level.ballRunning", "" )
        self.ballRunning = False
        try:
            # update level
            self.set_level( self.current_level+1 )
        except:
            print_exc()
        del self.threadLevel
        self.threadLevel = None


class onLevel( threading.Thread ):
    def __init__( self, game, lock ):
        threading.Thread.__init__( self )
        self.lock = lock
        self._stop = False

        self.game = game

        self.enemies = [] #max 3 any 1 min delay
        self.balls = [] #max 3
        self.bonus = [] #max 5
        self.fires = {} #max 3

    def new_enemy( self ):
        Id = len( self.enemies ) + 1
        if Id <= 2: self.enemies.append( Enemy( self, Id ) )

    def clonesBall( self ):
        # clone ball 1 = rect( x, y, w, h ), ( fpdx, fpdy )
        clone = None
        try:
            xbmcgui.lock()
            for ball in self.balls:
                if not ball.dead:
                    rect = ball.ballControl.getRect()
                    fpd = neg( ball.fpdx ), neg( ball.fpdy )
                    clone = rect, fpd
                    break
        except:
            print_exc()
        xbmcgui.unlock()
        if clone:
            self.new_ball( clone )

    def new_ball( self, clone=None ):
        Id = len( self.balls ) + 1
        #if Id <= 5:
        self.balls.insert( 0, Ball( self, Id, clone ) )

    def new_bonus( self, rect ):
        Id = len( self.bonus ) + 1
        #if Id <= 5:
        self.bonus.append( Bonus( self, rect, Id ) )

    def new_fire( self ):
        Id = len( self.fires ) + 1
        #bug + 1 :( 
        #if Id <= 2:
        self.fires[ Id ] = Fire( self, Id )

    def run( self ):
        self.lock.acquire()
        self.game.ballSpeed = 6
        self.new_ball()
        ballsOnScreen = 1
        enemyDelay = time()
        levelup = False
        while not self._stop:
            #xbmcgui.lock()
            try:
                while self.game.paused and not self._stop:
                    sleep( .02 )
                    continue
                ballsOnScreen = self.updates()
                if not ballsOnScreen: break
                # avec des enemies ca commence à ralentir :) trop
                #if not self.enemies or ( time() - enemyDelay ) > 5:
                #    self.new_enemy()
                #    self.new_ball()
                #    enemyDelay = time()
                if self.game.fireShots:# and len( self.fires ) < 2:
                    self.new_fire()
                    self.game.fireShots = 0
                #if not self.game.ballRunning:
                #    break
                if not self.game.totalWalls:
                    levelup = True
                    break
            except:
                print_exc()
            #xbmcgui.unlock()
            sleep( .01 )

        #removes all sprites
        self.updates( True )

        #if self.game.totalWalls:
        #    print "Thread-Game: Game Over"
        self.lock.release()

        if levelup:
            self.game.levelUp()
            print "Thread-Game: level up: ", self.game.current_level

        if not ballsOnScreen:
            self.game.addVausPlayers()
            del self.game.threadLevel
            self.game.threadLevel = None

    def stop( self ):
        self._stop = True

    def updates( self, remove=False ):
        # update ball
        ballsOnScreen = 0
        try:
            for ball in self.balls:
                try:
                    if remove: ball.stop()
                    if ball.update: ball.update()
                    if not ball.dead: ballsOnScreen += 1
                except:
                    pass
        except:
            print_exc()

        # update fire
        try:
            for fire in self.fires.values():
                try:
                    if remove: fire.stop()
                    if fire.update: fire.update()
                except:
                    pass
        except:
            print_exc()

        # update bonus
        try:
            for bonus in self.bonus:
                try:
                    if remove: bonus.stop()
                    if bonus.update: bonus.update()
                except:
                    pass
        except:
            print_exc()

        # update enemies
        try:
            for enemy in self.enemies:
                try:
                    if remove: enemy.stop()
                    if enemy.update: enemy.update()
                except:
                    pass
        except:
            print_exc()

        return ballsOnScreen
