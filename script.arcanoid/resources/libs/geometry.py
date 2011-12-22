"""
    based on pygame - Python Game Library
    by frost (passion-xbmc.org)
"""

#Modules general
import random
from math import *


class Error( Exception ):
    pass


try:
    triangular = random.triangular
except:
    def triangular( low=0.0, high=1.0, mode=None ):
        """random.triangular(...) not implanted in python 2.4
        Triangular distribution.

        Continuous distribution bounded by given lower and upper limits,
        and having a given mode value in-between.

        http://en.wikipedia.org/wiki/Triangular_distribution

        """
        u = random.random()
        #c = 0.5 if mode is None else (mode - low) / (high - low) # python 2.5 to 3.xx only
        if mode is None: c = 0.5 
        else: c = ( mode - low ) / ( high - low )
        if u > c:
            u = 1.0 - u
            c = 1.0 - c
            low, high = high, low
        return low + ( high - low ) * ( u * c ) ** 0.5


class Rectangle:
    def __init__( self, x, y, w, h ):
        self.x = x
        self.y = y
        self.w = w or 1
        self.h = h or 1
        self.width = self.w
        self.height = self.h

        self.top = self.y
        self.left = self.x
        self.bottom = self.top + self.height
        self.right = self.left + self.width

        self.centerx = self.left + int( self.width/2.0 )
        self.centery = self.top + int( self.height/2.0 )
        self.center = ( self.centerx, self.centery )
        self.size = ( self.width, self.height )

        self.topleft = ( self.left, self.top )
        self.topright = ( self.right, self.top )
        self.bottomleft = ( self.left, self.bottom )
        self.bottomright = ( self.right, self.bottom )

        self.midtop = ( self.centerx, self.top )
        self.midleft = ( self.left, self.centery )
        self.midbottom = ( self.centerx, self.bottom )
        self.midright = ( self.right, self.centery )

    def __repr__( self ):
        return "<rect(%d, %d, %d, %d)>" % ( self.x, self.y, self.w, self.h )


class Rect( Rectangle ):
    def __init__( self, x=0, y=0, w=0, h=0 ):
        Rectangle.__init__( self, x, y, w, h )

    def collidepoint( self, *xy ):
        """Rect.collidepoint

            test if a point is inside a rectangle
            Rect.collidepoint(x, y): return bool
            Rect.collidepoint((x,y)): return bool

            Returns true if the given point is inside the rectangle.

            A point along the right or bottom edge is not considered to be inside the rectangle.
            inside = x >= self.left and x < self.right and y >= self.top and y < self.bottom
        """
        if len( xy ) == 1:
            try:
                x, y = xy[ 0 ]
            except:
                raise Error, "bad point argument: %r" % ( xy[ 0 ], )
        else:
            try:
                x, y = xy
            except:
                raise Error, "bad coordinates: %r" % ( xy[ 0 ], )
        #for arkanoid include "right and bottom edge"
        inside = x >= self.left and x <= self.right and y >= self.top and y <= self.bottom
        return inside

    def colliderect( self, rect ):
        """Rect.colliderect

              test if two rectangles overlap
              Rect.colliderect(Rect): return bool

              Returns true if any portion of either rectangle overlap.
        """
        rectpos = [ rect.center, rect.midtop, rect.midleft, rect.midbottom, rect.midright, 
            rect.topleft, rect.topright, rect.bottomleft, rect.bottomright ]
        ret = self.collidelist( rectpos )
        return ret

    def collidelist( self, liste ):
        """Rect.collidelist

              test if one point in a list intersects
              Rect.collidelist(list): return index

              Test whether the point collides with any in a sequence of rectangles.
              The index of the first collision found is returned. If no collisions are found None is returned.
        """
        ret = None
        for count, xy in enumerate( liste ):
            if self.collidepoint( xy ):
                ret = count
                break
        return ret

    def collidelistall( self, liste ):
        """Rect.collidelistall

              test if all rectangles in a list intersect
              Rect.collidelistall(list): return indices

              Returns a list of all the indices that contain rectangles that collide with the Rect.
              If no intersecting rectangles are found, an empty list is returned.
        """
        indices = []
        for count, xy in enumerate( liste ):
            if self.collidepoint( xy ):
                indices.append( count )
        return indices

    def collidedict( self, dico ):
        """Rect.collidedict

              test if one rectangle in a dictionary intersects
              Rect.collidedict(dict): return (key, value)

              Returns the key and value of the first dictionary value that collides with the Rect.
              If no collisions are found, None is returned.

              Rect objects are not hashable and cannot be used as keys in a dictionary, only as values.
        """
        ret = None
        for key, value in dico.items():
            if self.colliderect( value ) is not None:
                ret = key, value
                break
        return ret

    def collidedictall( self, dico ):
        """Rect.collidedictall

              test if all rectangles in a dictionary intersect
              Rect.collidedictall(dict): return [(key, value), ...]

              Returns a list of all the key and value pairs that intersect with the Rect.
              If no collisions are found an empty dictionary is returned.

              Rect objects are not hashable and cannot be used as keys in a dictionary, only as values.
        """
        indices = []
        for key, value in dico.items():
            if self.colliderect( value ) is not None:
                indices.append( ( key, value ) )
        return indices

    def collidedirection( self, rect ):
        """Rect.collidedirection
        """
        direction = [ "center", "midtop", "midleft", "midbottom", "midright", "topleft", "topright", "bottomleft", "bottomright" ]
        index = self.colliderect( rect )
        if index is not None:
            return direction[ index ]


class Circle:
    def __init__( self, x, y, r, e=None ):
        self.coords = []
        self._origin = ( x, y, r, e )
        self.circle( x, y, r, e )

    def circle( self, posx, posy, radius, extent=None ):
        position = posx, posy
        angle = 0.0
        fullcircle = 360.0
        invradian = pi / ( fullcircle * 0.5 )
        if extent is None:
            extent = fullcircle
        frac = abs( extent ) / fullcircle
        steps = 1 + int( min( 11 + abs( radius ) / 6.0, 59.0 ) * frac )
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        distance = 2.0 * radius * sin( w2 * invradian )
        if radius < 0:
            distance, w, w2 = -distance, -w, -w2
        angle = ( angle + w2 ) % fullcircle
        for i in range( steps ):
            x0, y0 = start = position
            x1 = x0 + distance * cos( angle * invradian )
            y1 = y0 - distance * sin( angle * invradian )

            x0, y0 = position
            position = map( float, ( x1, y1 ) )
            dx = float( x1 - x0 )
            dy = float( y1 - y0 )
            distance2 = hypot( dx, dy )
            nhops = int( distance2 )
            try:
                for i in range( 1, 1+nhops ):
                    x, y = x0 + dx * i / nhops, y0 + dy * i / nhops
                    self.coords.append( ( x, y ) )
            except:
                pass
            angle = ( angle + w ) % fullcircle
        angle = ( angle + -w2 ) % fullcircle

    def __repr__( self ):
        return "<circle(%s,%s)>" % ( self._origin, self.coords )

'''
class Circle2:
    def __init__( self, x, y, w ):
        self.setorigin( x, y )
        self.width = w
        self._path = []
        self._angle = 0.0
        self.degrees()
        self.reset()
        self.circle()

    def degrees( self, fullcircle=360.0 ):
        """ Set angle measurement units to degrees.

        Example:
        >>> degrees()
        """
        # Don't try to change _angle if it is 0, because
        # _fullcircle might not be set, yet
        if self._angle:
            self._angle = ( self._angle / self._fullcircle ) * fullcircle
        self._fullcircle = fullcircle
        self._invradian = pi / ( fullcircle * 0.5 )

    def setorigin( self, x, y ):
        """ set origin coord.
        """
        #width = 720
        #height = 576
        #self._origin = float( width )/2.0, float( height )/2.0
        self._origin = float( x ), float( y )
        
    def reset( self ):
        """ Clear the screen, re-center the pen, and set variables to
        the default values.
        """
        self._position = self._origin
        self._angle = 0.0
        self._path = []

    def setx( self, xpos ):
        """ Set the turtle's x coordinate to be xpos.
        """
        x0, y0 = self._origin
        x1, y1 = self._position
        self._goto( x0+xpos, y1 )

    def sety(self, ypos):
        """ Set the turtle's y coordinate to be ypos.
        """
        x0, y0 = self._origin
        x1, y1 = self._position
        self._goto( x1, y0-ypos )

    def left( self, angle ):
        """ Turn left angle units (units are by default degrees,
        but can be set via the degrees() and radians() functions.)

        When viewed from above, the turning happens in-place around
        its front tip.
        """
        self._angle = ( self._angle + angle ) % self._fullcircle

    def right( self, angle ):
        """ Turn right angle units (units are by default degrees,
        but can be set via the degrees() and radians() functions.)

        When viewed from above, the turning happens in-place around
        its front tip.
        """
        self.left( -angle )

    def forward( self, distance ):
        """ Go forward distance steps.
        """
        x0, y0 = start = self._position
        x1 = x0 + distance * cos( self._angle*self._invradian )
        y1 = y0 - distance * sin( self._angle*self._invradian )
        self._goto( x1, y1 )

    def _goto( self, x1, y1 ):
        x0, y0 = self._position
        self._position = map( float, ( x1, y1 ) )
        dx = float( x1 - x0 )
        dy = float( y1 - y0 )
        distance = hypot( dx, dy )
        nhops = int( distance )
        try:
            for i in range( 1, 1+nhops ):
                x, y = x0 + dx*i/nhops, y0 + dy*i/nhops
                self._path.append( ( x, y ) )
        except:
            return

    def circle( self, radius=0, extent=None ):
        """ Draw a circle with given radius.
        The center is radius units left of the turtle; extent
        determines which part of the circle is drawn. If not given,
        the entire circle is drawn.

        If extent is not a full circle, one endpoint of the arc is the
        current pen position. The arc is drawn in a counter clockwise
        direction if radius is positive, otherwise in a clockwise
        direction.

        >>> circle(50)
        >>> circle(120, 180)  # half a circle
        """
        if not radius:
            radius = float( self.width )/2.0
        if extent is None:
            extent = self._fullcircle
        frac = abs( extent )/self._fullcircle
        steps = 1+int( min( 11+abs( radius )/6.0, 59.0 )*frac )
        w = 1.0 * extent/steps
        w2 = 0.5 * w
        l = 2.0 * radius * sin( w2*self._invradian )
        if radius < 0:
            l, w, w2 = -l, -w, -w2
        self.left( w2 )
        for i in range( steps ):
            self.forward( l )
            
            self.left( w )
        self.right( w2 )

    def __repr__( self ):
        return "<circle(%s)>" % repr( self._path )


'''
if  __name__ == "__main__":
    #print Rect( 0, 0, 0, 0 )
    circ = Circle( 680, 293, 6 )

    #print min( circ.coords ), max( circ.coords )

    rect = Rect( 600, 300, 80, 120 )
    point = rect.collidelistall( circ.coords )
    center = circ.coords[ int( len( point )/2 ) ]
    print "centerpoint", center
    for p in point:
        print circ.coords[ p ]

    #print rect
    #print rect.center

    #print rect.midtop
    #print rect.midleft
    #print rect.midbottom
    #print rect.midright

    print triangular()
