﻿"""
meCheckTexturePaths

ver.1.0.4 26 Jun 2013
  - fix for VRay

ver.1.0.3 20 Apr 2012
  - lookup for textures in mentalrayIblShape
  - texture types and attributes gathered from tuples list
  
ver.1.0.2 26 Jan 2012
  - lookup for textures in ImagePlanes
  - textures list splited to 3 frameLayout: 
    Image Planes, Maya Textures, MentalRay Textures
  - fix iconTextButton heigth for Maya2008
  
ver.1.0.0 30 Oct 2011
ver.0.0.1 28 Oct 2011

Author:

  Yuri Meshalkin (aka mesh)
  mesh@kpp.kiev.ua
  
  (c) Kiev Post Production 2011,2012

Description:

  This UI script shows lists of texture nodes
  (maya, mentalray) and imagePlanes with indictaion
  of MotFound/Absolute/Relative location. It helps to select
  texture nodes and to replace strings in texture names 

Usage:

  import meTools.meCheckTexturePaths as tx
  reload( tx )
  tx = tx.meCheckTexturePaths()

"""
import string
import maya.OpenMaya as OpenMaya
from functools import partial
import maya.cmds as cmds
import maya.mel as mel

from maya_ui_proc import *

self_prefix = 'meCheckTexturePaths_'
meCheckTexturePathsVer = "1.0.4"
meCheckTexturePathsMainWnd = "meCheckTexturePathsMainWnd"
meCheckTexturePathsReplaceWnd = "meCheckTexturePathReplaceWnd"
#
# meCheckTexturePaths
#
class meCheckTexturePaths ( object ) :
  #
  # __init__
  #
  def __init__ ( self, selection = '' ) :
    #print ">> meCheckTexturePaths: Class created"
    self.selection = selection
    self.winMain = ''
    self.winReplace = ''
    self.listTextures = ''
    self.rootDir = cmds.workspace ( q = True, rootDirectory = True )
    
    self.strToFind = getDefaultStrValue ( self_prefix, 'strToFind', '' )
    self.strToReplace = getDefaultStrValue ( self_prefix, 'strToReplace', '' )
    
    self.fileTextures = []
    self.mr_fileTextures = []
    self.imagePlanes = []
    
    self.ui = self.setupUI ()
    self.jobOnDelete = cmds.scriptJob ( uiDeleted = [ self.winMain , self.onDeleteMainWin ] )
  #
  # __del__
  #  
  def __del__ ( self ) :
    #print( ">> meCheckTexturePaths: Class deleted" )
    if cmds.scriptJob ( exists = self.jobOnDelete ) :
      cmds.scriptJob( kill = self.jobOnDelete, force = True )
  #
  # onStrToFindChanged
  #  
  def onStrToFindChanged ( self, value ) : self.strToFind = self.setDefaultStrValue ( 'strToFind', value )
  #
  # onStrToReplaceChanged
  #  
  def onStrToReplaceChanged ( self, value ) : self.strToReplace = self.setDefaultStrValue ( 'strToReplace', value )
  #
  # onFileNameChanged
  #  
  def onFileNameChanged ( self, fileNodeName, attr, value ) :
    #print( ">> meCheckTexturePaths: onFileNameChanged %s = %s" % ( fileNodeName, value ) )
    cmds.setAttr ( fileNodeName + '.' + attr, value, type = 'string' ) # ".fileTextureName"
  #
  # selectFileNode
  #  
  def selectFileNode ( self, fileNodeName ) : cmds.select ( fileNodeName, r = True )
  #
  # drawFrameLayout
  # 
  def drawFrameLayout ( self, frameTitle, textureTypeAttrList ) : # , attrNameList
    cw1 = 100
    cw2 = 60
    cmds.setParent ( self.listTextures )
    
    cmds.frameLayout ( label = frameTitle, borderVisible = True, borderStyle = 'etchedIn', marginHeight = 0, cll = True, cl = False )
    cmds.columnLayout ( columnAttach=( 'left', 0 ), rowSpacing = 0, adjustableColumn = True ) 
    
    for i in range ( len ( self.fileTextures ) ) :
      labelType = 'Not Found'
      labelColor = ( 0.5, 0.0, 0.0 )
      fileNodeName = self.fileTextures [ i ]
      fileNodeType = cmds.objectType ( fileNodeName )
      fileName = ''
      
      for ( textureType, attrName ) in textureTypeAttrList :
        #print "textureType = %s attrName = %s" % ( textureType, attrName )
        
        if fileNodeType != textureType : continue  
        
        fileTextureName = cmds.getAttr( fileNodeName + "." + attrName )
        print ( '>> fileTextureName = %s' ) % fileTextureName
        if fileTextureName is not None and fileTextureName != '' :
          fileName = str ( fileTextureName )
          if cmds.file ( fileTextureName, q = True, exists = True ) :
            labelType = 'Absolute'
            labelColor = ( 1.0, 0.5, 0.0 )
            fileName = cmds.workspace ( projectPath = fileTextureName )
            if isRelative ( fileName ) :
              labelType = 'Relative'
              labelColor = (0.0, 0.5, 0.0)  
      
        cmds.rowLayout ( numberOfColumns = 2, columnWidth1 = cw2, adjustableColumn2 = 2 )
        cmds.iconTextButton ( style = 'textOnly', label = labelType, width = cw2, h = 16, bgc = labelColor )
        cmds.textFieldButtonGrp ( cw = ( 1, cw1 ), adj = 2, 
                                 label = fileNodeName, 
                                 buttonLabel = 'select', 
                                 text = fileName, 
                                 cc = partial ( self.onFileNameChanged, fileNodeName, attrName ),
                                 bc = partial ( self.selectFileNode, fileNodeName ) )
        cmds.setParent ( '..' )      
  #
  # refreshUI
  #  
  def refreshUI ( self, param ) :
    #
    special_type_str_list = [ 'imagePlane' ]  
    if cmds.getAttr ( 'defaultRenderGlobals.currentRenderer' ) == 'mentalRay' :
      special_type_str_list.append ( 'mentalrayIblShape' )  
    self.fileTextures = cmds.ls ( textures = True, type = special_type_str_list ) 
    
    print self.fileTextures
     
    if cmds.columnLayout( self.listTextures, q=True, numberOfChildren=True ) > 0 :
      controls = cmds.columnLayout( self.listTextures, q=True, childArray=True )
      for i in range( len( controls ) ):
        cmds.deleteUI( controls[ i ] )
      
    self.drawFrameLayout ( ' Image Planes ', [ ( 'imagePlane', 'imageName' ) ] )
    self.drawFrameLayout ( ' Maya Textures ', [ ( 'file', 'fileTextureName' ) ] )
    if cmds.getAttr ( 'defaultRenderGlobals.currentRenderer' ) == 'mentalRay' :
      self.drawFrameLayout ( ' MentalRay Textures ', [ ( 'mentalrayTexture', 'fileTextureName' ), ( 'mentalrayIblShape', 'texture' ) ] )
  #
  # setupUI      
  #        
  def setupUI ( self ) :
    #
    cw1 = 100
    cw2 = 60
    self.deleteUI( True )
    # Main window setup
    self.winMain = cmds.window( meCheckTexturePathsMainWnd, 
                                title="meCheckTexturePaths ver." + meCheckTexturePathsVer, 
                                menuBar=True,
                                retain=False,
                                widthHeight=(500, 400) )   
    
          
    form = cmds.formLayout( 'f0', numberOfDivisions=100 )  
    proj = cmds.columnLayout( 'c0', columnAttach=('left',0), rowSpacing=2, adjustableColumn=True, height=32 )
    cmds.textFieldGrp( cw=( 1, cw2 ), columnAlign=( 1, 'center' ), adj=2, label=" Project ", text=self.rootDir, editable=False )
    cmds.setParent( '..' )
    
    scr = cmds.scrollLayout( 'scr', childResizable=True )
    self.listTextures = cmds.columnLayout( 'c1',  rowSpacing=0, adjustableColumn=True ) #columnAttach=('left',0 ), bgc=(0.5, 0.5, 0.0)

    self.refreshUI( True )

    cmds.setParent( form )
                                 
    btn_rep = cmds.button( label = 'Replace ...', command = self.onReplace )
    btn_ref = cmds.button( label = 'Refresh', command = self.refreshUI )
    btn_cls = cmds.button( label = 'Close', command = self.deleteUI )
    
    cmds.formLayout(  form, edit=True, 
                      attachForm=( ( proj, 'top',    0 ), 
                                   ( proj, 'left',    0 ), 
                                   ( proj, 'right',    0 ), 
                                   ( scr, 'left',    0 ), 
                                   ( scr, 'right',    0 ),  
                                   ( btn_cls,   'bottom', 0 ),
                                   ( btn_rep,   'bottom', 0 ),
                                   ( btn_ref,   'bottom', 0 ),
                                   ( btn_rep,   'left',   0 ),
                                   ( btn_cls,   'right',  0 )
                                 ),  
                      attachControl=( ( scr , 'top', 0, proj ),
                                      ( scr , 'bottom', 0, btn_rep ),
                                      ( btn_ref, 'left', 0, btn_rep ), 
                                      ( btn_ref, 'right', 0, btn_cls ) 
                                    ), 
                      attachPosition=( 
                                       ( btn_rep , 'right', 0, 33 ),
                                       ( btn_ref , 'right', 0, 66 ),
                                       ( btn_cls, 'left', 0, 66 )
                                      )  
                   )
   
    cmds.showWindow( self.winMain )
    return form
  #
  # onDeleteMainWin
  #    
  def onDeleteMainWin( self ) :
    #print (">> meCheckTexturePaths: onDeleteMainWin() " )
    #cmds.delete( self.listTextures)
    self.deleteReplaceUI( True )
  #
  # deleteReplaceUI
  #    
  def deleteReplaceUI ( self, param ) :
    #
    winReplace = meCheckTexturePathsReplaceWnd 
    if cmds.window( winReplace, exists=True ): cmds.deleteUI( winReplace, window=True )
    if cmds.windowPref( winReplace, exists=True ): cmds.windowPref( winReplace, remove=True )
  #
  # deleteUI
  #  
  def deleteUI ( self, param ) :
    #
    winMain = meCheckTexturePathsMainWnd
    if cmds.window ( winMain, exists = True ) : cmds.deleteUI ( winMain, window = True )
    if cmds.windowPref ( winMain, exists = True ) : cmds.windowPref ( winMain, remove = True )
  #
  # doFindReplace
  #
  def doFindReplace ( self, param ) :
    #
    if self.strToFind != '' :
      print ( ">> self.strToFind = %s self.strToReplace = %s" ) % ( self.strToFind, self.strToReplace )
      
      for i in range ( len( self.fileTextures ) ):  
        fileNodeName = self.fileTextures [ i ]
        fileNodeType = cmds.objectType ( fileNodeName )
        
        if fileNodeType == 'file' or fileNodeType == 'mentalrayTexture' : attrName = "fileTextureName" 
        elif fileNodeType == 'imagePlane' : attrName = "imageName" 
        else : continue  
        
        fileTextureName = cmds.getAttr ( fileNodeName + "." + attrName )
        
        if fileTextureName is None : fileName = ''
        else : fileName = str ( fileTextureName )
        newName = str ( fileName ).replace ( str ( self.strToFind ), str ( self.strToReplace ), 1 )
        if newName != fileName :
          # print fileNodeName + "." + attrName
          # ??? It is strange, but folder renaming doesn't work wor ImagePlane's "imageName" attribute... 
          cmds.setAttr( fileNodeName + "." + attrName, newName, type="string" )
          print ">> fileName = %s new = %s" % ( fileName, newName )
      self.refreshUI ( True )
  #
  # onReplace
  #    
  def onReplace ( self, param ) :
    #
    cw1 = 100
    cw2 = 60
    
    if cmds.window ( meCheckTexturePathsReplaceWnd, exists = True ) : 
      cmds.deleteUI ( meCheckTexturePathsReplaceWnd, window = True )
      
    self.winReplace = cmds.window ( meCheckTexturePathsReplaceWnd, 
                                title = 'Find and Replace', 
                                menuBar = False,
                                retain = False,
                                widthHeight = ( 400, 100 ) )   

    form = cmds.formLayout ( 'f0', numberOfDivisions = 100 )  
    cmds.formLayout ( form, e = True, width = 500 )
    col = cmds.columnLayout ( 'c0', columnAttach = ( 'left',0 ), rowSpacing = 2, adjustableColumn = True, height = 40 )
    cmds.textFieldGrp ( 'find_str', cw = (  1, cw1 ), adj = 2, label = 'Find string : ', text = self.strToFind, cc = self.onStrToFindChanged )
    cmds.textFieldGrp ( 'replace_str', cw=( 1, cw1 ), adj = 2, label = 'Replace with : ', text = self.strToReplace, cc = self.onStrToReplaceChanged )
    cmds.setParent ( '..' )
    #cmds.text( label='' )
    btn_rep = cmds.button ( label = 'Replace ...', command = self.doFindReplace )
    btn_cls = cmds.button ( label = 'Close', command = self.deleteReplaceUI )

    cmds.formLayout ( form, edit = True,
                     attachForm = [ ( col, 'top', 10 ), 
                                    ( col, 'left', 0 ), 
                                    ( col, 'right', 0 ), 
                                    ( btn_rep, 'left', 0 ), 
                                    ( btn_cls , 'right', 0 ), 
                                    ( btn_cls, 'bottom', 0 ),
                                    ( btn_rep, 'bottom', 0 )
                                 ],
                     
                     attachControl = [ ( col, 'bottom', 0, btn_rep ), 
                                       ( btn_cls, 'left', 0, btn_rep )
                                   ],
                     attachPosition = [ 
                                       ( btn_rep, 'right', 0, 50 ), 
                                       ( btn_cls, 'left',0, 50 )
                                    ]
                   )

    cmds.showWindow( self.winReplace)
    
print 'meCheckTexturePaths sourced ...'   