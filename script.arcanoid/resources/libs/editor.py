"""
    by frost (passion-xbmc.org)
"""

#Modules general
import os
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui

#Modules Customs
import sprites
import arkanoid
import utilities


CWD = os.getcwd().rstrip( ";" )
MEDIAS_PATH = utilities.MEDIAS_PATH
BASE_RESOURCE_PATH = utilities.BASE_RESOURCE_PATH


class levelEditor( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )

    def onInit( self ):
        self.onReset()

    def onReset( self ):
        self.stage = [ 0 ] * 260
        self.stageBG = ""
        self.wallSelect = ""
        self.wallType = 0
        self.stageName = "N/A"
        try:
            self.clearList()
            self.setProperty( "editor.level.name", self.stageName )
            self.getControl( 150 ).reset()
            self.getControl( 250 ).reset()
            self.getControl( 350 ).reset()
            self.getControl( 450 ).reset()

            for count in range( 6 ):
                if count: 
                    icon = os.path.join( MEDIAS_PATH, "BG%s.png" % str( count ) )
                    list_item = xbmcgui.ListItem( "BG [%s]" % str( count ), "", icon, icon )
                else:
                    list_item = xbmcgui.ListItem( "BG [None]" )
                self.getControl( 450 ).addItem( list_item )

            for key, value in sprites.wallsValues.items():
                icon = ( "", os.path.join( MEDIAS_PATH, value[ 0 ] ) )[ bool( value[ 0 ] ) ]
                label2 = ( "%i PTS" % value[ 1 ], "Indestructible" )[ key == 10 ]
                item = xbmcgui.ListItem( str( key ), label2, icon, icon )
                self.getControl( 150 ).addItem( item )

            [ self.getControl( 350 ).addItem( xbmcgui.ListItem( str( i+1 ) ) ) for i in range( 100 ) ]

            for wall in self.stage:
                label = str( wall+1 )
                self.getControl( 250 ).addItem( xbmcgui.ListItem( label ) )
                self.addItem( xbmcgui.ListItem( label ) )

        except:
            print_exc()

    def setStage( self ):
        try:
            walls = sprites.wallsValues
            self.clearList()
            self.setProperty( "editor.level.name", self.stageName )
            self.getControl( 250 ).reset()
            self.getControl( 350 ).reset()

            [ self.getControl( 350 ).addItem( xbmcgui.ListItem( str( i+1 ), "", self.stageBG ) ) for i in range( 100 ) ]

            for wall in self.stage:
                label = str( wall+1 )
                icon = walls[ wall ][ 0 ]
                self.getControl( 250 ).addItem( xbmcgui.ListItem( label, "", icon ) )
                self.addItem( xbmcgui.ListItem( label ) )

        except:
            print_exc()

    def setStageName( self ):
        try:
            kb = xbmc.Keyboard( self.stageName, "Edit New Name" )
            kb.doModal()
            if kb.isConfirmed():
                name = kb.getText()
                if bool( name ):
                    self.stageName = name
                    self.setProperty( "editor.level.name", self.stageName )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 450:
                pos = self.getControl( 450 ).getSelectedPosition()
                self.stageBG = ( "", os.path.join( MEDIAS_PATH, "BG%s.png" % str( pos ) ) )[ pos != 0 ]
                [ self.getControl( 350 ).getListItem( i ).setIconImage( self.stageBG ) for i in range( 100 ) ]

            elif controlID == 150:
                wall_item = self.getControl( 150 ).getSelectedItem()
                self.wallType = int( wall_item.getLabel() )
                self.wallSelect = sprites.wallsValues[ self.wallType ][ 0 ]
                [ self.getListItem( i ).setIconImage( self.wallSelect ) for i in range( 260 ) ]
                self.setFocusId( 50 )

            elif controlID == 50:
                pos = self.getCurrentListPosition()
                wall_item = self.getControl( 250 ).getListItem( pos )
                self.wallSelect = sprites.wallsValues[ self.wallType ][ 0 ]
                wall_item.setIconImage( self.wallSelect )
                self.stage[ pos ] = self.wallType

            elif controlID == 121:
                self.setStageName()

            elif controlID == 122:
                #load custom stage
                stg = utilities.getBrowseDialog( os.path.join( BASE_RESOURCE_PATH, "custom_levels" )+os.sep,
                    heading="Select Your Stage", mask=".stage" )
                if os.path.isfile( stg ):
                    self.loadStage( stg )
                    self.setStage()

            elif controlID == 123:
                if sum( self.stage ):
                    self.saveStage()

            elif controlID == 124:
                self.onReset()

            elif controlID == 125:
                #load original stage or tournament
                stage_path = utilities.getBrowseDialog( os.path.join( BASE_RESOURCE_PATH, "media", "stages" )+os.sep,
                    heading="Select Original Stage", dlg_type=2, shares="pictures", use_thumbs=True )
                level_id = os.path.splitext( os.path.basename( stage_path ) )[ 0 ].split( "_" )[ -1 ]
                if level_id.isdigit():
                    level_id = int( level_id )
                    self.stage = arkanoid.Levels()[ level_id ]
                    self.stageBG = "BG%i.png" % arkanoid.getLevelBackground( level_id )
                    self.stageName = ( "Arkanoid %i" % level_id, "Tournament %i" % level_id )[ "tournament" in os.path.basename( stage_path ).lower() ]
                    self.setStage()

            elif controlID == 320:
                self.closeEditor()
        except:
            print_exc()

    def loadStage( self, stage_path="" ):
        try:
            if not stage_path: stage_path = os.path.join( BASE_RESOURCE_PATH, "custom_levels", "test.stage" )
            f = open( stage_path, "r" )
            bg, stage = eval( f.read() )
            f.close()
            #test valide stage and background
            error_info = "Bad file! %s" % stage_path
            if not len( stage ) == 260: raise error_info
            for colrow in stage:
                if not ( 0 <= colrow <= 10 ): raise error_info
            self.stage = stage
            if os.path.exists( bg ): self.stageBG = bg
            self.stageName = os.path.splitext( os.path.basename( stage_path ) )[ 0 ]
        except:
            print_exc()
            self.onReset()

    def saveStage( self ):
        try:
            if xbmcgui.Dialog().yesno( "Arkanoid Stage Editor", "Confirm save stage!", "", "", "Pass", "Save" ):
                dir_path = os.path.join( BASE_RESOURCE_PATH, "custom_levels" )
                if not os.path.exists( dir_path ): os.makedirs( dir_path )
                # dialog edtit name
                if not self.stageName or self.stageName == "N/A":
                    self.setStageName()
                if self.stageName and self.stageName != "N/A":
                    f = open( os.path.join( dir_path, "%s.stage" % self.stageName ), "w" )
                    f.write( repr( ( self.stageBG, self.stage ) ) )
                    f.close()
        except:
            print_exc()

    def onAction( self, action ):
        try:
            if action in [ 9, 117 ] and self.getFocusId() == 50:
                pos = self.getCurrentListPosition()
                wall_item = self.getControl( 250 ).getListItem( pos )
                wall_item.setIconImage( "" )
                self.stage[ pos ] = 0

            elif action == 10:
                self.closeEditor()
        except:
            print_exc()

    def closeEditor( self ):
        if sum( self.stage ):
            self.saveStage()
        self.close()

