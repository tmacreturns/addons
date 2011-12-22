
#Modules General
import os
import sys
import time
from traceback import print_exc

import elementtree.ElementTree as ET

#Modules XBMC
import xbmc
import xbmcgui


def parse_description_xml():
    try:
        # load and parse description.xml file
        feed = open( os.path.join( os.getcwd(), "description.xml" ) )
        tree = ET.parse( feed )
        feed.close()
        elems = tree.getroot()

        # required tags
        # (required) guuid: unique identifier of this addon guuids can be generated online at sites such as http://www.famkruithof.net/uuid/uuidgen
        guid = elems.findtext( "guid" )
        #(required) type:
        type = { 1: "visualization", 2: "skin", 3: "pvrdll", 4: "script", 5: "scraper", 6: "screensaver",
            7: "plugin-pvr", 8: "plugin-video", 9: "plugin-music", 10: "plugin-program", 11: "plugin-pictures",
            12: "plugin-weather" }.get( int( elems.findtext( "type" ) ), "unknown" ).title()
        # (required) Title
        title = elems.findtext( "title" )
        # (required) Major.minor.build
        version = elems.findtext( "version" )
        # (required) author name & email. at least one author name is required
        authors = [ elem.attrib for elem in elems.find( "authors" ) ]
        # (required) Short description of addon.
        summary = elems.findtext( "summary" )
        # optional tags
        # Longer description of addon. Usage instructions should go here if required.
        try: description = elems.findtext( "description" )
        except: description = ""
        # user defined tags
        try: tags = " / ".join( [ elem.text for elem in elems.find( "tags" ) ] )
        except: tags = ""
        # minimum revision of xbmc your addon will run on. Leave blank all for revisions
        try: minrevision = elems.findtext( "minrevision" )
        except: minrevision = ""
        # patforms compatible with your addon. xbox, osx, windows, linux, or all
        try: platforms = " / ".join( [ elem.text for elem in elems.find( "platforms" ) ] )
        except: platforms = ""
        # list any dependancies (such as another addon, your addon may have. minversion and maxversion are optional
        try: dependencies = [ ( elem.attrib, elem.text ) for elem in elems.find( "dependencies" ) ]
        except: dependencies = []
        # (optional) Whatever is put in disclaimer will be shown before download in an ok/cancel dialog. Keep it short and to the point.
        try: disclaimer = elems.findtext( "disclaimer" )
        except: disclaimer = ""
        # (optional) The License the addon is released under.
        try: license = elems.findtext( "license" )
        except: license = ""

        del feed, tree, elems, elem
        #for key in locals().keys():
        #    print key
        return locals()
    except:
        print_exc()


class Info( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )

        self.infos = parse_description_xml()

    def onInit( self ):
        try:
            icon = os.path.join( os.getcwd(), "default.tbn" )
            self.getControl( 48 ).reset()
            listitem = xbmcgui.ListItem( self.infos[ "title" ], "", icon, icon )
            for key, value in self.infos.items():
                if isinstance( value, str ):
                    listitem.setProperty( key, value )
            authors = " / ".join( [ "%s, %s" % ( author[ "name" ], author[ "email" ] ) for author in self.infos[ "authors" ] ] )
            listitem.setProperty( "authors", authors )
            listitem.setProperty( "dependencies", "" )
            listitem.setProperty( "revision", sys.modules[ "__main__" ].__svn_revision__ )
            listitem.setProperty( "filepath", os.getcwd() )
            self.getControl( 48 ).addItem( listitem )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID == 12:
            self._close_dialog()

    def onAction( self, action ):
        if action in ( 9, 10 ):
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .4 )
        self.close()
