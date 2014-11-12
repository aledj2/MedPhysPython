# this module is called to store points in an array.
#This version is used in conjunction with the phidgets spatial sensor

import vtk

class linedrawer():
        def __init__(self):
                self.points=vtk.vtkPoints()
                #self.accelerationarray=[]                                                                            
                
        def addPoint(self,point):
                self.points.InsertNextPoint(point) 
                
        #=======================================================================
        # def accelarray(self, index):
        #     #if plot.p1.accelerometer == True:
        #         self.accelerationarray.append(index)
        #         acceldata = self.accelerationarray
        #         #print acceldata
        #         #print "acceleration array:"+str(self.accelerationarray)
        #=======================================================================
                
