'''
Created on 13 Jun 2014
Add new actors as required sphere or new arrow.
Scrap STL object opening if the object cannot be scaled down 

@author: rodney
'''

import wx
import vtk
import os
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor

class interWin(wx.Panel): # Interactive window (interWin)
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        # Default object to display 
        self.stlObject = vtk.vtkSTLReader()
    
        # Use \\ for the path name instead of \ for vtk to recognise the default file
        self.stlObject.SetFileName("C:\\Users\\user\\workspace\\arrow.stl")
     
        # Create a mapper and an actor 
        self.mainMapper = vtk.vtkPolyDataMapper()        
        self.mainMapper.SetInputConnection(self.stlObject.GetOutputPort())
        self.mainActor = vtk.vtkActor()
        self.mainActor.SetMapper(self.mainMapper)
        self.mainActor.GetProperty().BackfaceCullingOff()
    
        self.widget = wxVTKRenderWindowInteractor(self, -1)
        self.widget.Enable(1)
        self.widget.AddObserver("ExitEvent", lambda o,e,f=self: f.Close())
        self.style = vtk.vtkInteractorStyleTrackballActor()
        self.widget.SetInteractorStyle(self.style)
        
        # Binds events to the functions created 
        self.widget.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.widget.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleDown)
        self.widget.Bind(wx.EVT_MOTION, self.onMotion)
        self.widget.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.widget.Bind(wx.EVT_MIDDLE_UP, self.onMiddleUp)
        self.widget.Bind(wx.EVT_KEY_DOWN, self.kDown)
        self.widget.Bind(wx.EVT_RIGHT_UP, self.onRightUp)
        self.widget.Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)        
        self.trackMotion = False
        self.trackpos = False        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.widget, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
        self.isploted = False  
          
        # Open window and create a renderer
        # to interact with the scene using the mouse use an instance of vtkRenderWindowInteractor.
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(.1, .2, .3) # Background colour dark blue         
        self.widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # Add actor to render window 
        #self.renderer.GetActors().AddActor(self.mainActor)
        self.renderer.AddActor(self.mainActor)
       
        # Setup orientation markers 
        self.axes = vtk.vtkAxesActor()
        self.marker = vtk.vtkOrientationMarkerWidget()
        self.marker.SetInteractor(self.widget._Iren)
        self.marker.SetOrientationMarker(self.axes)
        self.marker.SetViewport(0.75,0,1,0.25)
        self.marker.SetEnabled(1)
        
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.isploted = True
        
        # Getting points when the actor is moved with the mouse 
        self.pointcatcher = self.linedrawer()
        self.linesPolyData = vtk.vtkPolyData()

    def onMiddleDown(self,e):
            # middle button down 
            self.trackpos = True
            e.Skip()
             
    def onLeftDown(self,e):
            #left mouse button down
            self.trackMotion = True
            e.Skip()
            
    def onRightDown(self,e):
            #right mouse button down
            e.Skip()
             
    def onMotion(self,e):
            #left mouse button down
            if self.trackMotion == True:
                    e.Skip()
                    self.Orientation = self.mainActor.GetOrientation()
                    self.GetGrandParent().statusbar.SetStatusText("Orientation is " + str(self.Orientation))

            elif self.trackpos == True: 
                    e.Skip()
                    self.position = self.mainActor.GetPosition()
                    print self.position
                    self.GetGrandParent().statusbar.SetStatusText("Position is " + str(self.position))
                    coordgrab=tuple(self.position)
                    xC=float(coordgrab[0])
                    yC=float(coordgrab[1])
                    zC=float(coordgrab[2])
                    self.pointcatcher.addPoint((xC,yC,zC))
                    # Create a cell array to store the lines in and add the lines to it
                    lines = vtk.vtkCellArray()
                    
                    # Create a polydata to store everything in
                    # Add the points to the dataset
                    self.linesPolyData.SetPoints(self.pointcatcher.points)
                    
                    # Add the lines to the dataset
                    self.linesPolyData.SetLines(lines)
                     
                    self.l = vtk.vtkPoints.GetNumberOfPoints(self.pointcatcher.points)

                    lines.InsertNextCell(self.l)
                    for i in range(self.l):
                        lines.InsertCellPoint(i)
                        
    def kDown(self,e):
        self.key = e.GetKeyCode()    
        if self.key == 77:
            print "you pressed m"
            # Setup actor and mapper
            mapper = vtk.vtkPolyDataMapper()
            if vtk.VTK_MAJOR_VERSION <= 5:
                mapper.SetInput(self.linesPolyData)
            else:
                mapper.SetInputData(self.linesPolyData)
               
            self.lineActor = vtk.vtkActor()
            self.lineActor.SetMapper(mapper)
            self.lineActor.GetProperty().SetColor(0.1,0.1,0.1)
            self.lineActor.GetProperty().SetLineWidth(30)
   
            self.renderer.AddActor(self.lineActor)
            self.widget.GetRenderWindow().Render()
        # Remove the line actor created by adding poly data to linesPolydata
        # using the delete key and the left mouse button     
        if self.key == wx.WXK_DELETE:
            print "Would you like to delete actor? Press left mouse button with Del key"
            if self.trackMotion == True:
                self.renderer.RemoveActor(self.lineActor)
                self.widget.GetRenderWindow().Render()
        # Change the actor to an arrow when the A key is pressed 
        if self.key == 65:
            print"you pressed A"
            # Arrow actor 
            self.arrow = vtk.vtkArrowSource()
            
            #Smooth out the arrow 
            self.arrow.SetTipResolution (100)
            self.arrow.SetShaftResolution(100)
            self.arrow.InvertOn()
            
            # Set the actor to the main Actor and the main mapper to replace the current Actor
            self.mainMapper.SetInputConnection(self.arrow.GetOutputPort())
            self.actor = self.mainActor
            self.actor.SetMapper(self.mainMapper)
                
            #add the actors to the scene
            self.renderer.AddActor(self.actor)
            self.widget.GetRenderWindow().Render()
            
        # Change the actor to a sphere when the S key is pressed 
        if self.key == 83:
            print "you pressed S"
            #Sphere actor 
            self.sphereSource = vtk.vtkSphereSource()
            self.sphereSource.SetCenter(0.0, 0.0, 0.0)
            self.sphereSource.SetRadius(0.1)
            self.sphereSource.SetThetaResolution(100)
            self.sphereSource.SetPhiResolution(100)
            
            # use the main mapper
            self.mainMapper.SetInputConnection(self.sphereSource.GetOutputPort())
            
            #create an actor
            self.actor = self.mainActor
            self.actor.SetMapper(self.mainMapper)
            self.renderer.AddActor(self.actor)
            self.widget.GetRenderWindow().Render()
            
        # Write the contents of linesPolyData array to a file 
        if self.key == 87:
            print "you pressed W"
            writer = vtk.vtkPolyDataWriter()
            writer.SetFileName("test3.vtk")
            if vtk.VTK_MAJOR_VERSION <= 5:
                writer.SetInput(self.linesPolyData)
            else:
                writer.SetInputData(self.linesPolyData)
            writer.Write()
        if self.key == 82:
            print "you pressed R"
            reader = vtk.vtkPolyDataReader()
            reader.SetFileName("test3.vtk")
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            self.renderer.AddActor(actor)
            self.widget.GetRenderWindow().Render()
            
    def onLeftUp(self,e):
            #left mouse button down
            self.trackMotion = False
            e.Skip()
            
    def onRightUp(self,e):
            #right mouse button down
            e.Skip()
             
    def onMiddleUp(self,e):
            #left mouse button down
            self.trackpos = False
            e.Skip()
                 
    def openSTL(self,stlFile):
            self.stlObject.SetFileName(stlFile)
            self.widget.GetRenderWindow().Render()
            self.mainActor.SetScale(0.1,0.1,0.1)
            self.renderer.ResetCamera()
    class linedrawer():
        def __init__(self):
                self.points = vtk.vtkPoints()
                                                                            
        def addPoint(self,point):
                self.points.InsertNextPoint(point) 
                
class viewFrame(wx.Frame):
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(650,600), style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU|
                  wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        
        #add menu 
        fileMenu = wx.Menu()
        menuOpenSTL = fileMenu.Append(wx.ID_OPEN, "&Open STL","Open an STL file")
        menuExit = fileMenu.Append(wx.ID_EXIT,"E&xit","Exit the program")
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"&File")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU,self.onOpenSTL,menuOpenSTL)
        self.Bind(wx.EVT_MENU,self.onExit,menuExit)
        
        #Split mainframe and add panels
        self.sp = wx.SplitterWindow(self)
        self.screen = interWin(self.sp)        
        self.p2 = wx.Panel(self.sp,style=wx.SUNKEN_BORDER)# (self.controls)
        self.sp.SplitHorizontally(self.screen,self.p2,470)
        
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Just started ")
    
    # Function to open a .stl file      
    def onOpenSTL(self,e):
            self.statusbar.SetStatusText("Ah! You are trying to load a new file!")
            self.dirName = ''
            dlg = wx.FileDialog(self, "Choose a file", self.dirName,"","*.stl", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.fileName = dlg.GetFilename()
                self.dirName = dlg.GetDirectory()
                self.statusbar.SetStatusText("You want to open " + os.path.join(self.dirName, self.fileName))
                self.screen.openSTL(os.path.join(self.dirName,self.fileName))
            dlg.Destroy()
            
    # def write poly data to a file dialog box for user input 
    #===========================================================================
    # def wriPointsFile(self,e):
    #     self.statusbar.SetStatusText("Would you like to create a new file?")
    #     self.dirName = ''
    #     dlg = wx.FileDialog(self, "Choose a file", self.dirName,"","*.stl", wx.OPEN)
    #     if dlg.ShowModal() == wx.ID_OK:
    #         self.fileName = dlg.GetFilename()
    #         self.dirName = dlg.GetDirectory()
    #         self.statusbar.SetStatusText("You want to open " + os.path.join(self.dirName, self.fileName))
    #         self.screen.openSTL(os.path.join(self.dirName,self.fileName))
    #     dlg.Destroy()
    #===========================================================================

    # def read poly data from a file to draw the path taken by an actor using dialog box 
    def rePointsFile(self,e):
        self.statusbar.SetStatusText("Ah! You are trying to load a new file!")
        self.dirName = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirName,"","*.stl", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            self.statusbar.SetStatusText("You want to open " + os.path.join(self.dirName, self.fileName))
            self.screen.openSTL(os.path.join(self.dirName,self.fileName))
        dlg.Destroy()
        
    def onExit(self,e):
            self.Close(True)
                     
app = wx.App(redirect=False)
frame = viewFrame(None,"Lights, Cameras, Action")
frame.Show()
app.MainLoop()