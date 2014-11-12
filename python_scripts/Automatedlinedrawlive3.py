#This version can grab the coordinates of an actor via a button, take coordinates from a dialog box or from a file 
#and draw a line with them

import wx
import os
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import linedrawer
import numpy as np
import SpatialAled2 as S


class p1(wx.Panel):
        def __init__(self,parent):
                wx.Panel.__init__(self, parent)

        #to interact with the scene using the mouse use an instance of vtkRenderWindowInteractor. 
                self.widget = wxVTKRenderWindowInteractor(self, -1)
                self.widget.Enable(1)
                self.widget.AddObserver("ExitEvent", lambda o,e,f=self: f.Close())
                self.trackballStyle = vtk.vtkInteractorStyleTrackballCamera()
                self.widget.SetInteractorStyle(self.trackballStyle)
                self.sizer = wx.BoxSizer(wx.VERTICAL)
                self.sizer.Add(self.widget, 1, wx.EXPAND)
                self.SetSizer(self.sizer)
                self.Layout()
                self.isploted = False
                self.accelerometer = False
                
            
        def renderthis(self):
            # open a window and create a renderer
            self.ren = vtk.vtkRenderer()
            self.widget.GetRenderWindow().AddRenderer(self.ren)
            
            # Background colour lightgrey
            self.ren.SetBackground(0.9,0.9,0.9)
            
            #create a X,Y,Z axes to show 3d position:
            # create axes variable and load vtk axes actor
            self.axes = vtk.vtkAxesActor()
            self.marker = vtk.vtkOrientationMarkerWidget()
            
            # set the interactor. self.widget._Iren is inbuilt python mechanism for current renderer window.
            self.marker.SetInteractor(self.widget._Iren )
            self.marker.SetOrientationMarker(self.axes )
            
            # set size and position of window (Xmin,Ymin,Xmax,Ymax)
            self.marker.SetViewport(0.75,0,1,0.25)
            
            #Allow user input
            self.marker.SetEnabled(1)

            # #settings for renderer window 
            self.ren.ResetCamera()
            self.ren.ResetCameraClippingRange()         
            self.isplotted = True
            self.p=0


                             
#set up a new class to control the control panel which houses buttons and user inputs (not mouse) 
class TestFrame(wx.Frame):
            def __init__(self,parent,title):
                wx.Frame.__init__(self,parent,title=title,size=(650,600), style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
                self.sp = wx.SplitterWindow(self)
                self.p1 = p1(self.sp)
                self.p2 = wx.Panel(self.sp,style=wx.SUNKEN_BORDER)
                
                #split the screen horizontally
                self.sp.SplitHorizontally(self.p1,self.p2,500)
                
                #create status bar with initial message
                self.statusbar = self.CreateStatusBar()
                self.statusbar.SetStatusText("Click on load data set to select file")

                #create a button to get a file input
                self.getfilebut = wx.Button(self.p2,-1,"load dataset", size=(150,20),pos=(10,10))
                self.getfilebut.Bind(wx.EVT_BUTTON,self.GetFile)
                    
                self.linebut = wx.Button(self.p2,-1,"plot line", size=(150,20),pos=(170,10))
                self.linebut.Bind(wx.EVT_BUTTON,self.lineplot)
                
                self.trackpos = False
                self.liveinputbut = wx.Button(self.p2,-1,"live input", size=(150,20),pos=(330,10))
                self.liveinputbut.Bind(wx.EVT_BUTTON,S.liveinput)
                self.liveinputbut.Bind(wx.EVT_BUTTON,self.onLiveinput)
            
                self.stopinputbut = wx.Button(self.p2,-1,"stop input", size=(150,20),pos=(490,10))
                self.stopinputbut.Bind(wx.EVT_BUTTON,S.stopinput)
                
                #create a function which will hold points for an updating line
                self.pointcatcher = linedrawer.linedrawer()
                
                # Create a polydata to store everything in
                self.linesPolyData = vtk.vtkPolyData()
                
            def onLiveinput(self,e):
                self.trackpos = True 
                print "tracking accelerometer"
                e.Skip()
                
            def onStopinput(self,e):
                self.trackpos = False 
                                 
            # this function is called by the getfilebut above. It opens a dialog box which asks for the frequency followed by a second dialog which
            # asks for the file containing raw acceleration file            
            def GetFile(self,event):
                
                        dlg = wx.TextEntryDialog (self.p2, 'Enter frequency rate (Hz) Default =250',"Frequency","250", style=wx.OK)
                        dlg.ShowModal() 
                        self.freqin=float(dlg.GetValue())
                        dlg.Destroy()
                        if not self.p1.isploted:
                            self.p1.renderthis()
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
             
                            self.p1.ren.AddActor(self.lineActor)
                            self.p1.widget.GetRenderWindow().Render()
 
                        # this converts the frequncy in Hz to the time taken at each measurement. freqsq is used in the calculations below
                        freq= 1/self.freqin
                        freqsq=freq*freq
                          
                        #create an array to hold the values from accleration file
                        self.accelx=[]
                        self.accely=[]
                        self.accelz=[] 
                                
                        #open file and for each line split into x, y, z. taking i>1 excludes the column headers
                        if self.trackpos == True:
                            for list in S.accelerationarray:
                                x = float(list[0])
                                y = float(list[1])
                                z = float(list[2])
                                self.accelx.append(x)
                                self.accely.append(y)
                                self.accelz.append(z)

                             
                        #need average score for first 10 values for x,y and z. np.mean is a numpy function
                        xavg=np.mean(self.accelx [0:9])
                        yavg=np.mean(self.accely [0:9])
                        zavg=np.mean(self.accelz [0:9])
                        
                        # subtract the average values from each read to normalise. normx1 is an array of all x values. this feeds normx which is 
                        #populated by these values minus the average. np.array is a numpy function
                        normx1=np.array(self.accelx)
                        normx=[normx1-xavg]
                        normy1=np.array(self.accely)
                        normy=[normy1-yavg]
                        normz1=np.array(self.accelz)
                        normz=[normz1-zavg]                
                         
                        # turn into velocity (o.5(a(t^2)). uses two values as above.uses freqsq
                        velx1=np.array(normx)
                        velx=[0.5*(velx1*freqsq)]
                        vely1=np.array(normy)
                        vely=[0.5*(vely1*freqsq)]
                        velz1=np.array(normz)
                        velz=[0.5*(velz1*freqsq)]

                        #cumulative velocity. creates an array where each element is the running total of the array (Numpy function)
                        cumvelx = np.cumsum(velx)
                        cumvely = np.cumsum(vely)
                        cumvelz = np.cumsum(velz)
                        print cumvelx 
                        print cumvely 
                        print cumvelz 
                         
                        #distance. cumulative velocity times the frequency. timesd by 100,000 to visualise without zooming in.
                        disx=cumvelx*freq*100000
                        disy=cumvely*freq*100000
                        disz=cumvelz*freq*100000
                         
                        #cumulative distance. again uses numpy cumsum function
                        cumdisx =np.cumsum(disx)
                        cumdisy =np.cumsum(disy)
                        cumdisz =np.cumsum(disz)

                        #combine all three arrays (x,Y,Z) back into a single array with each element a tuple of the three arrays 
                        #uses zip function
                        distancecood= zip(cumdisx,cumdisy,cumdisz)
                        print "distancecood="+str(distancecood)
                         
                        # iterate through the array adding each element to the linedrawer array
                        for i in distancecood:
                            self.pointcatcher.addPoint(i)     
                        # Create a cell array to store the lines in and add the lines to it
                        lines=vtk.vtkCellArray()
                        
                        # Add the points to the dataset
                        self.linesPolyData.SetPoints(self.pointcatcher.points)
                        # Add the lines to the dataset
                        self.linesPolyData.SetLines(lines)
                         
                        self.l=vtk.vtkPoints.GetNumberOfPoints(self.pointcatcher.points)
                        print "number of points in points array:"+str(self.l)
                        lines.InsertNextCell(self.l)
                        for i in range(self.l):
                            lines.InsertCellPoint(i)
                    
        # this function is called from the above button and renders the line which is created from the 
        #inputs/captured from the arrow position
            def lineplot(self,event):
                print "plot"

app = wx.App(redirect=False)
frame = TestFrame(None,"Track the movement")
frame.Show()
app.MainLoop()