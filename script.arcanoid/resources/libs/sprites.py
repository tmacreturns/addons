"""
    by frost (passion-xbmc.org)
"""

#Modules General
import os
import math
import random
from time import sleep
from threading import Timer
from traceback import print_exc

#Modules XBMC
#import xbmc
import xbmcgui

#Modules Customs
import arkanoid
import utilities
from geometry import *


SFX = utilities.SFX
MEDIAS_PATH = utilities.MEDIAS_PATH

BALL_SPEED_START = 6
BALL_SPEED_MAX = 18

wallsValues = { 0: ( "",    0 ), # dummy
    1:  ( "Red.png",       90 ),
    2:  ( "Green.png",     80 ),
    3:  ( "Blue.png",     100 ),
    4:  ( "Yellow.png",   120 ),
    5:  ( "Silver.png",    50 ), # 50 pts x round number
    6:  ( "Pink.png",     110 ),
    7:  ( "White.png",     50 ),
    8:  ( "LightBlue.png", 70 ),
    9:  ( "Orange.png",    60 ),
    10: ( "Gold.png",       0 ) } # indestructible


def ball_speed( s, d ):
    if s == 3:
        return s
    s += ( d * 10 )
    if s > BALL_SPEED_MAX:
        s = BALL_SPEED_MAX
    #if d > .1:
    #    s = BALL_SPEED_START
    return s


class CustomControlImage( xbmcgui.ControlImage ):
    """ControlImage class.

        ControlImage(x, y, width, height, filename[, colorKey, aspectRatio, colorDiffuse])

        x              : integer - x coordinate of control.
        y              : integer - y coordinate of control.
        width          : integer - width of control.
        height         : integer - height of control.
        filename       : string - image filename.
        colorKey       : [opt] hexString - (example, '0xFFFF3300')
        aspectRatio    : [opt] integer - (values 0 = stretch (default), 1 = scale up (crops), 2 = scale down (black bars)
        colorDiffuse   : hexString - (example, '0xC0FF0000' (red tint))

        *Note, You can use the above as keywords for arguments and skip certain optional arguments.
               Once you use a keyword, all following arguments require the keyword.
               After you create the control, you need to add it to the window with addControl().

        example:
          - self.image = xbmcgui.ControlImage(100, 250, 125, 75, aspectRatio=2)
    """
    def __init__( self, *args, **kwargs ):
        xbmcgui.ControlImage.__init__( self, *args, **kwargs )

    def getRect( self ):
        x, y = self.getPosition()
        w, h = self.getWidth(), self.getHeight()
        return Rect( x, y, w, h )

    def getCircle( self, radius=None, extent=None ):
        x, y = self.getPosition()
        w, h = self.getWidth(), self.getHeight()
        if radius is None:
            #set radius based on minimun half diameter
            radius = float( ( w, h )[ h < w ] ) / 2.0
        # return [ ( x, y ), ... ]
        return Circle( x + int( radius ), y + h, radius, extent )


class Wall:
    def __init__( self, x, y, w, h, type, constants_level, genpos ):
        level, mode, custom = constants_level

        self.rect = Rect( x, y, w, h )
        self.x, self.y = self.rect.x, self.rect.y
        self.w, self.h = self.rect.w, self.rect.h
       
        self.type = type
        self.shots_destroy = ( ( 1, arkanoid.getHitsToDestroy( level ) )[ type == 5 ], 0 )[ type == 10 ]

        walls_values = wallsValues#()
        self.image = walls_values[ self.type ][ 0 ]
        self.score = walls_values[ self.type ][ 1 ]
        del walls_values

        # gold_vs_gold = "left", "top", "right", "bottom"
        self.vs_gold = [ False, False, False, False ]
        if self.type == 10:
            if mode in [ 1, 4 ]:
                level = arkanoid.Levels()[ level ]
            elif mode in [ 2, 5 ]:
                level = arkanoid.TournamentLevels()[ level ]
            else:
                level = custom[ 1 ]
            if genpos > 0:        self.vs_gold[ 0 ] = level[ genpos -  1 ] == 10
            if genpos - 13 > 0:   self.vs_gold[ 1 ] = level[ genpos - 13 ] == 10
            if genpos + 1 < 260:  self.vs_gold[ 2 ] = level[ genpos +  1 ] == 10
            if genpos + 13 < 260: self.vs_gold[ 3 ] = level[ genpos + 13 ] == 10


class Ball:
    speed = BALL_SPEED_START
    anglel = 45
    angleh = 135
    def __init__( self, onlevel, Id, clone=None, image="Ball.gif" ):
        self._stop = False
        self.Id = Id

        self.clone = clone # rect( x, y, w, h ), ( fpdx, fpdy )
        self.image = image
        self.containers = onlevel
        self.game = self.containers.game
        self.window = self.game.window
        self.gamePlay = self.window.screenGamePlay

        self.addBall()
        self.update = self.start

    def addBall( self ):
        self.ballControl = CustomControlImage( self.game.getCurrentVausRect().x + self.window.defaultBallRect.x,
            self.window.defaultBallRect.y, self.window.defaultBallRect.w, self.window.defaultBallRect.h,
            os.path.join( MEDIAS_PATH, self.image ) )
        self.window.addControl( self.ballControl )
        self.ballControl.setVisibleCondition( 'IsEmpty(Container.Property(game.paused))' )
        if self.clone:
            # on va la remettre visible dans une fraction de seconde
            self.ballControl.setVisible( 0 )

    def setPos( self ):
        #print int( self.fpx ), int( self.fpy )
        self.ballControl.setPosition( int( self.fpx ), int( self.fpy ) )

    def remove_control( self ):
        #self.delay += 1
        if not self._stop:
            self.ballControl.setVisible( 0 )
            try:
                xbmcgui.lock()
                self.window.removeControl( self.ballControl )
            except: print_exc()
            xbmcgui.unlock()
            self._stop = True
        #return self.delay == 25

    def stop( self ):
        self.update = self.remove_control

    def start( self ):
        self.dead = False
        self._stop = False
        self.newStart = True
        if not self.clone:
            self.ballRect = self.ballControl.getRect()
        else:
            self.ballRect = self.clone[ 0 ]
        vausRect = self.game.getCurrentVausRect()
        self.defaultVausTop = vausRect.top
        self.ballRect.x = vausRect.centerx

        self.fpx = self.ballRect.x
        self.fpy = self.ballRect.y
        if not self.clone:
            self.fpdx = 0.5
            self.fpdy = 1.5
        else:
            self.fpdx = self.clone[ 1 ][ 0 ]
            self.fpdy = self.clone[ 1 ][ 1 ]

        self.setPos()
        if self.clone:
            self.ballControl.setVisible( 1 )
        self.update = self.slide

    def setfp( self ):
        """use whenever usual integer rect values are adjusted"""
        self.fpx = self.ballRect.x
        self.fpy = self.ballRect.y

    def setint( self ):
        """use whenever floating point rect values are adjusted"""
        self.ballRect.x = self.fpx
        self.ballRect.y = self.fpy

    def new_angle( self, factor ):
        angle = math.radians( self.angleh - factor * ( self.angleh - self.anglel ) )
        self.speed = ball_speed( self.game.ballSpeed, .2 )
        self.fpdx = self.speed * math.cos( angle )
        self.fpdy = -self.speed * math.sin( angle )
        
    def slide( self ):
        # bounce from vaus
        bounce_from_vaus = False
        self.ballRect = self.ballControl.getRect()
        if int( self.fpy + self.ballRect.h ) >= self.defaultVausTop > int( self.fpy ):
            vausRect = self.game.getCurrentVausRect()
            #if vausRect.colliderect( self.ballRect ) and self.fpdy < 0:
            #   print "frappe par le bas! ou ball pris dans le vaus :))", self.fpdy
            #   #sleep( 1 )
            if self.fpdy > 0 and vausRect.colliderect( self.ballRect ) is not None:
                utilities.SFX( "ping3.wav" )
                #if self.game.vausHasCatch and not self.newStart:
                #    self.ballControl.setVisible( 0 )
                #    self.window.setProperty( "level.ballRunning", "" )
                #    sleep( .5 )
                #    self.game.ballRunning = False
                #    self._stop = True
                self.newStart = False
                ballpos = self.ballRect.right - vausRect.left - 1
                ballmax = self.ballRect.width + vausRect.width - 2
                factor = float( ballpos ) / ballmax
                self.new_angle( factor )
                if self.speed == 3:
                    self.speed = BALL_SPEED_START
                    self.game.ballSpeed = self.speed 
                bounce_from_vaus = True

        # usual movement
        self.fpx = self.fpx + self.fpdx
        self.fpy = self.fpy + self.fpdy
        self.setint()

        if bounce_from_vaus:
            #sert a rien de continuer, car pas de wall proche
            self.setfp()
            self.setPos()
            return

        '''
        # ball vs ball, optional
        try:
            if len( self.containers.balls ) > 1:
                actual_rect = Rect( self.ballRect.x, self.ballRect.y, self.ballRect.w, self.ballRect.h )
                for ball in self.containers.balls:
                    if hasattr( ball, 'ballRect' ) and self.Id != ball.Id:
                        if ball.dead: continue
                        vs = Rect( ball.ballRect.x, ball.ballRect.y, ball.ballRect.w, ball.ballRect.h )
                        point = actual_rect.colliderect( vs )
                        if point is not None:
                            if point == 0:#"center":
                                self.fpx = vs.x - ( vs.w/2 )
                            if point == 1:#"midtop":
                                self.fpy = vs.y - vs.h
                            if point == 2:#"midleft":
                                self.fpx = vs.x - vs.w
                            if point == 3:#"midbottom":
                                self.fpy = vs.y + vs.h
                            if point == 4:#"midright":
                                self.fpx = vs.x + vs.w
                            if point == 5:#"topleft":
                                self.fpx, self.fpy = vs.topleft
                            if point == 6:#"topright":
                                self.fpx, self.fpy = vs.topright
                            if point == 7:#"bottomleft":
                                self.fpx, self.fpy = vs.bottomleft
                            if point == 8:#"bottomright":
                                self.fpx, self.fpy = vs.bottomright
                            self.fpdx, self.fpdy = -self.fpdx, -self.fpdy
        except:
            print_exc()
        '''

        # bounce from borders gameplay
        if self.ballRect.left <= self.gamePlay.left:
            # |O
            utilities.SFX( "ping1.wav" )
            self.ballRect.x = self.gamePlay.left + 1
            self.setfp()
            self.fpdx = -self.fpdx
            return self.setPos()
        elif self.ballRect.right >= self.gamePlay.right:
            # O|
            utilities.SFX( "ping1.wav" )
            self.ballRect.x = self.gamePlay.right - 1 - self.ballRect.w
            self.setfp()
            self.fpdx = -self.fpdx
            return self.setPos()
        elif self.ballRect.top <= self.gamePlay.top:
            # _
            # O
            utilities.SFX( "ping1.wav" )
            self.ballRect.y = self.gamePlay.top + 1
            self.setfp()
            self.fpdy = -self.fpdy
            return self.setPos()
        elif self.ballRect.top >= self.gamePlay.bottom:
            # O
            # ¯
            ballsOnScreen = 0
            for ball in self.containers.balls:
                if not ball.dead and self.Id != ball.Id:
                    ballsOnScreen += 1
            if not ballsOnScreen:
                utilities.SFX( "dead.wav" )
                self.window.setProperty( "vaus.statut", "BOOM" )
                sleep( 1 )
                self.window.setProperty( "vaus.statut", "NORMAL" )

                self.game.ballRunning = False
                self.window.setProperty( "level.ballRunning", "" )
            else:
                utilities.SFX( "bang.wav" )
            self.stop()
            self.dead = True
            return 
            #pass
            #elif self.ballRect.bottom >= self.gamePlay.bottom:
            # for testing not dead ball
            # O
            # ¯
            #utilities.SFX( "dead.wav" )
            #self.ballRect.y = self.gamePlay.bottom - 1 - self.ballRect.h
            #self.setfp()
            #self.fpdy = -self.fpdy
            #return self.setPos()
            #pass

        # bounce from walls
        try:
            # wallsCollided detect pas tous le temps tout les walls :( merde
            #tb = Rect( self.ballRect.x, self.ballRect.y, self.ballRect.w, self.ballRect.h )
            #wallsDict = dict( [ (k,v.rect) for k,v in self.game.wallsControls.items() ] )
            #wallsCollided = tb.collidedictall( wallsDict )
            #if wallsCollided:
            #    print "wallsCollided", wallsCollided

            # destroy walls
            gold_new_angle = False
            for key in self.game.wallsControls.keys():
                wall = self.game.wallsControls[ key ]
                if wall is None: continue
                issilver = wall.type == 5
                isgold = wall.type == 10
                wall = wall.rect
                tb = Rect( self.ballRect.x, self.ballRect.y, self.ballRect.w, self.ballRect.h )
                # []-wall, O-ball
                left = right = up = down = 0
                #[ tb.midleft, tb.midtop, tb.midbottom, tb.midright ]
                #[ tb.topleft, tb.topright, tb.bottomleft, tb.bottomright ]
                if isgold and wall.collidelist( [ tb.midleft, tb.midtop, tb.midbottom, tb.midright ] ) is not None:
                    goldWall = self.game.wallsControls[ key ]
                    # []O
                    if self.ballRect.left <= wall.right < self.ballRect.right:
                        if goldWall.vs_gold[ 2 ]: # ball entre deux gold
                            if self.fpdy > 0: # ball direction vers le bas
                                self.ballRect.y = wall.top - 1 - self.ballRect.h # on la place au dessus
                            else: #sinon ball vers le haut
                                self.ballRect.y =  wall.bottom + 1 # on la place au dessous
                            if not gold_new_angle:
                                # on change une seule fois l'angle
                                gold_new_angle = True
                                self.fpdy = -self.fpdy
                        else:
                            # pas de vs gold, on fait comme un block normal
                            right = 1
                            self.ballRect.x = wall.right + 1
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdx = -self.fpdx
                        self.setfp()
                    # O[]
                    elif self.ballRect.left < wall.left <= self.ballRect.right:
                        if goldWall.vs_gold[ 0 ]:
                            if self.fpdy > 0:
                                self.ballRect.y = wall.top - 1 - self.ballRect.h
                            else:
                                self.ballRect.y = wall.bottom + 1
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdy = -self.fpdy
                        else:
                            left = -1
                            self.ballRect.x = wall.left - 1 - self.ballRect.w
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdx = -self.fpdx
                        self.setfp()
                    #  O
                    # [¯]
                    elif self.ballRect.top < wall.top >= self.ballRect.bottom:
                        if goldWall.vs_gold[ 1 ]:
                            if self.fpdx > 0:
                                self.ballRect.x = wall.left - 1 - self.ballRect.w
                            else:
                                self.ballRect.x = wall.right + 1
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdx = -self.fpdx
                        else:
                            up = -1
                            self.ballRect.y = wall.top - 1 - self.ballRect.h
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdy = -self.fpdy
                        self.setfp()
                    # [_]
                    #  O
                    elif self.ballRect.bottom > wall.bottom <= self.ballRect.top:
                        if goldWall.vs_gold[ 3 ]:
                            if self.fpdx > 0:
                                self.ballRect.x = wall.left - 1 - self.ballRect.w
                            else:
                                self.ballRect.x = wall.right + 1
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdx = -self.fpdx
                        else:
                            down = 1
                            self.ballRect.y = wall.bottom + 1
                            if not gold_new_angle:
                                gold_new_angle = True
                                self.fpdy = -self.fpdy
                        self.setfp()
                    utilities.SFX( "ping3.wav" )

                elif wall.collidelist( [ tb.midleft, tb.midtop, tb.midbottom, tb.midright ] ) is not None:
                    #print key, wall
                    # O[]
                    if self.ballRect.left < wall.left <= self.ballRect.right:
                        self.ballRect.x = wall.left - 1 - self.ballRect.w
                        self.setint()
                        left = -1
                    #  O
                    # [¯]
                    if self.ballRect.top < wall.top >= self.ballRect.bottom:
                        self.ballRect.y = wall.top - 1 - self.ballRect.h
                        self.setint()
                        up = -1
                    # []O
                    if self.ballRect.left <= wall.right < self.ballRect.right:
                        self.ballRect.x = wall.right + 1
                        self.setint()
                        right = 1
                    # [_]
                    #  O
                    if self.ballRect.bottom > wall.bottom <= self.ballRect.top:
                        self.ballRect.y = wall.bottom + 1
                        self.setint()
                        down = 1

                    self.game.setCollideWall( key, 1 )
                    if not isgold and not issilver:
                        self.containers.new_bonus( wall )

                # Si la balle est invitée à aller dans deux directions, alors on change pas de direction.
                dx, dy = ( left + right ), ( up + down )
                if dx is not 0:
                    #if isgold: self.fpdx = -self.fpdx
                    #else:
                    self.fpdx = dx * abs( self.fpdx )
                if dy is not 0:
                    #if isgold: self.fpdy = -self.fpdy
                    #else:
                    self.fpdy = dy * abs( self.fpdy )

        except:
            print_exc()
        self.setPos()


class Enemy:
    speed = 5
    anglel = 40
    angleh = 135
    def __init__( self, onlevel, Id, images=[ "cubes.gif", "pyramid.gif", "sphere.gif" ] ):
        self._stop = False
        self.Id = Id
        self.dead = False

        self.containers = onlevel
        self.game = self.containers.game
        self.window = self.game.window
        self.gamePlay = self.window.screenGamePlay

        self.defaultEnemyRect = random.choice( [ self.window.defaultEnemyRect1, self.window.defaultEnemyRect2 ] )
        self.image = random.choice( images )
        
        self.addEnemy()
        self.update = self.start

    def addEnemy( self ):
        self.enemyControl = CustomControlImage( self.defaultEnemyRect.x, self.defaultEnemyRect.y,
            self.defaultEnemyRect.w, self.defaultEnemyRect.h, os.path.join( MEDIAS_PATH, self.image ) )
        self.window.addControl( self.enemyControl )
        self.enemyControl.setVisibleCondition( 'IsEmpty(Container.Property(game.paused))' )

    def setPos( self ):
        #print int( self.fpx ), int( self.fpy )
        self.enemyControl.setPosition( int( self.fpx ), int( self.fpy ) )
        if self.dead or self.image == "boom.gif":
            self.stop()

    def remove_control( self ):
        #self.delay += 1
        if not self._stop:
            self.enemyControl.setVisible( 0 )
            try:
                xbmcgui.lock()
                self.window.removeControl( self.enemyControl )
            except: print_exc()
            xbmcgui.unlock()
            self._stop = True
        #return self.delay == 25

    def stop( self ):
        self.update = self.remove_control

    def start( self ):
        self._stop = False
        self.enemyRect = self.enemyControl.getRect()
        #vausRect = self.game.getCurrentVausRect()
        #self.defaultVausTop = vausRect.top

        self.fpx = self.enemyRect.x
        self.fpy = self.enemyRect.y
        self.fpdx = -random.uniform( 0.5, 5 )
        self.fpdy =  random.uniform( 1.0, 4 )

        self.setPos()
        self.update = self.slide

    def setfp( self ):
        """use whenever usual integer rect values are adjusted"""
        self.fpx = self.enemyRect.x
        self.fpy = self.enemyRect.y

    def setint( self ):
        """use whenever floating point rect values are adjusted"""
        self.enemyRect.x = self.fpx
        self.enemyRect.y = self.fpy

    def slide( self ):
        self.enemyRect = self.enemyControl.getRect()
        # usual movement
        self.fpx = self.fpx + self.fpdx
        self.fpy = self.fpy + self.fpdy
        self.setint()

        # bounce from borders gameplay
        if self.enemyRect.left <= self.gamePlay.left:
            # |O
            self.enemyRect.x = self.gamePlay.left + 1
            self.setfp()
            self.fpdx = -self.fpdx
            return self.setPos()
        elif self.enemyRect.right >= self.gamePlay.right:
            # O|
            self.enemyRect.x = self.gamePlay.right - 1 - self.enemyRect.w
            self.setfp()
            self.fpdx = -self.fpdx
            return self.setPos()
        elif self.enemyRect.top <= self.gamePlay.top:
            # _
            # O
            self.enemyRect.y = self.gamePlay.top + 1
            self.setfp()
            self.fpdy = -self.fpdy
            return self.setPos()
        elif self.enemyRect.bottom >= self.gamePlay.bottom:
            # O
            # ¯
            self.enemyRect.y = self.gamePlay.bottom - 1 - self.enemyRect.h
            self.setfp()
            self.fpdy = -self.fpdy
            return self.setPos()

        te = Rect( self.enemyRect.x, self.enemyRect.y, self.enemyRect.w, self.enemyRect.h )
        wallsDict = dict( [ (k, v.rect) for k, v in self.game.wallsControls.items() ] )
        wallsCollided = te.collidedictall( wallsDict )
        if wallsCollided:
            if len( wallsCollided ) > 1:
                self.fpdy = -self.fpdy
            else:
                self.fpdx = -self.fpdx
        self.setPos()


class Fire:
    speed = 6
    def __init__( self, onlevel, Id ):
        self._stop = False
        self.Id = Id

        self.containers = onlevel
        self.game = self.containers.game
        self.window = self.game.window
        self.gamePlay = self.window.screenGamePlay

        #delay to remove control
        self.delay = 0

        self.addFire()
        self.update = self.start
        self.update()

    def addFire( self, image="VausFireLaser.png" ):
        x, y = self.game.getCurrentVausRect().x, self.window.defaultFireRect.y 
        w, h = self.window.defaultFireRect.w, self.window.defaultFireRect.h
        self.fire = CustomControlImage( x, y, w, h, os.path.join( MEDIAS_PATH, image ) )
        self.window.addControl( self.fire )
        self.fire.setVisibleCondition( 'IsEmpty(Container.Property(game.paused))' )

    def remove_control( self ):
        self.delay += 1
        if not self._stop:
            self.fire.setVisible( 0 )
            try:
                xbmcgui.lock()
                self.window.removeControl( self.fire )
                #print self.Id, "self.window.removeControl( self.fire )"
            except: print_exc()
            xbmcgui.unlock()
            #del self.containers.fires[ self.Id ]
            self._stop = True
        return self.delay == 25

    def stop( self ):
        self.update = self.remove_control
        #self._stop = True

    def setPos( self ):
        #print int( self.fpx ), int( self.fpy )
        self.fire.setPosition( int( self.fpx ), int( self.fpy ) )
        if not self._stop and int( self.fpy ) < self.gamePlay.top:
            self.stop()

    def start( self ):
        self._stop = False
        self.fireRect = self.fire.getRect()
        vausRect = self.game.getCurrentVausRect()
        self.fireRect.left = self.fireRect.left + 2
        self.fireRect.right = self.fireRect.right - 2

        self.fpx = vausRect.x
        self.fpy = self.fireRect.y
        self.fpdy = -self.speed

        utilities.SFX( "laser.wav" )
        self.setPos()
        self.update = self.slide

    def slide( self ):
        try:
            self.fpy += self.fpdy
            #check for collision ( left|right, top )
            collided = False
            for key in self.game.wallsControls.keys():
                wall = self.game.wallsControls[ key ]
                if wall is None: continue
                issilver = wall.type == 5
                isgold = wall.type == 10
                wall = wall.rect
                if wall.collidelist( [ ( self.fireRect.left, self.fpy ), ( self.fireRect.right, self.fpy ) ] ) is not None:
                    self.fpy = wall.bottom
                    self.setPos()
                    self.game.setCollideWall( key )
                    if not isgold and not issilver:
                        self.containers.new_bonus( wall )
                    collided = True
                    #if not want double hits break
                    #break

            if collided:
                self.fire.setVisible( 0 )
                self.stop()

            if len( self.containers.enemies ) > 1:
                for enemy in self.containers.enemies:
                    collided = False
                    try:
                        if enemy.enemyRect.collidelist( [ ( self.fireRect.left, self.fpy ), ( self.fireRect.right, self.fpy ) ] ) is not None:
                            if not enemy.dead:
                                enemy.image = "boom.gif"
                                enemy.enemyControl.setImage( os.path.join( MEDIAS_PATH, enemy.image ) )
                                utilities.SFX( "bang.wav" )
                                enemy.dead = True
                                collided = True
                                break
                    except:
                        pass#print_exc()

                if collided:
                    self.fire.setVisible( 0 )
                    self.stop()
        except:
            print_exc()
        self.setPos()


class Bonus:
    speed = 5
    def __init__( self, onlevel, rect, Id ):
        self._stop = False
        self.Id = Id
        self.bonusRect = rect

        self.containers = onlevel
        self.game = self.containers.game
        self.window = self.game.window
        self.gamePlay = self.window.screenGamePlay

        # 1: "Catch.gif", 
        self.capsules = { 2: "Disruption.gif", 3: "Enlarge.gif",
            4: "Laser.gif", 5: "Player.gif", 6: "Slow.gif" }#, 7: "Wrap.gif"

        self.setCapsule()

    def setCapsule( self ):
        self.update = None
        self.capsule = self.getCapsule()
        if self.capsule:
            self.addBonus()
            self.update = self.start
            self.update()
        else:
            self._stop = False

    def getCapsule( self, round=0 ):
        caps = self.capsules.keys()
        chance = 2
        caps += [ "" ] * chance * len( caps )
        random.shuffle( caps )
        return random.sample( caps, 1 )[ 0 ]

    def addBonus( self ):
        image = self.capsules[ self.capsule ]
        x, y = self.bonusRect.x, self.bonusRect.y 
        w, h = self.bonusRect.w, self.bonusRect.h
        self.bonus = CustomControlImage( x, y, w, h, os.path.join( MEDIAS_PATH, image ) )
        self.window.addControl( self.bonus )
        self.bonus.setVisibleCondition( 'IsEmpty(Container.Property(game.paused))' )

        self.bonusRect = self.bonus.getRect()

    def remove_control( self ):
        self.vausCatch = None
        if not self._stop:
            self.bonus.setVisible( 0 )
            try:
                xbmcgui.lock()
                self.window.removeControl( self.bonus )
            except: print_exc()
            xbmcgui.unlock()
            self._stop = True

    def stop( self ):
        self.update = self.remove_control

    def setPos( self ):
        #print int( self.fpx ), int( self.fpy )
        self.bonus.setPosition( int( self.fpx ), int( self.fpy ) )
        if not self._stop and int( self.fpy ) > self.gamePlay.bottom:
            self.stop()

    def start( self ):
        self.vausCatch = None
        self._stop = False
        self.bonusRect = self.bonus.getRect()

        self.fpx = self.bonusRect.x
        self.fpy = self.bonusRect.y
        self.fpdy = self.speed

        self.setPos()
        if self.game.totalWalls > 1:
            self.update = self.slide
        else:
            self.update = self.remove_control

    def slide( self ):
        try:
            self.fpy += self.fpdy
            self.setPos()

            vausRect = self.game.getCurrentVausRect()
            if self.fpy+self.bonusRect.h >= vausRect.top:
                #check for vaus catch
                if vausRect.colliderect( self.bonus.getRect() ) is not None:
                    self.vausCatch = self.capsule

            if self.vausCatch is not None:
                self.setVausCatch()
        except:
            print_exc()

    def setVausCatch( self ):
        try:
            self.game.ballSpeed = 6
            self.game.vausHasCatch = False
            self.window.setProperty( "vaus.statut", "NORMAL" )
            if self.game.vaus_statut == "BIG" and self.vausCatch != 3:
                SFX( "vausUnZoom.wav" )
            self.game.vaus_statut = "NORMAL"
            if self.vausCatch == 1:
                self.game.vausHasCatch = True
            elif self.vausCatch == 2:
                self.containers.clonesBall()
            elif self.vausCatch == 3:
                self.game.vaus_statut = "BIG"
                self.window.setProperty( "vaus.statut", self.game.vaus_statut )
                SFX( "vausZoom.wav" )
            elif self.vausCatch == 4:
                self.game.vaus_statut = "LASER"
                self.window.setProperty( "vaus.statut", self.game.vaus_statut )
            elif self.vausCatch == 5:
                self.game.vausPlayers += 1
                self.window.vausPlayersContainer.addItem( xbmcgui.ListItem() )
                SFX( "playerbonus.wav" )
            elif self.vausCatch == 6:
                self.game.ballSpeed = 3
            # add + 1000 pts
            self.game.player_score += 1000
            self.window.setProperty( "score.player", str( self.game.player_score ) )
            if self.game.player_score > self.game.highscore:
                self.game.highscore = self.game.player_score
                self.window.setProperty( "score.highscore", str( self.game.highscore ) )
        except:
            print_exc()
        self.stop()
