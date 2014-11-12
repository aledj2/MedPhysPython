import numpy as np
import linedrawer2
import Automatedlinedrawfromacceldata230614 as plot

        
class accel2dist():   
        def __init__(self):             
                # this transforms the acceleration into distance
                
                self.pointcatcher = linedrawer2.linedrawer()
                #self.dialog = plot.TestFrame()
                
                #this converts the frequncy in Hz to the time taken at each measurement. freqsq is used in the calculations below
                #print freqin
                freq= 1/(self.freqin)
                print freq
                freqsq=freq*freq
                
                #create an array to hold the values from acceleration file
                self.accelx=[]
                self.accely=[]
                self.accelz=[]
                
                #open file and for each line split into x, y, z. taking i>1 excludes the column headers
                accelfile = open(self.infile,'r')
                #print "acceleration file opened:"+accelfile
                for i, line in enumerate(accelfile):
                    if i > 1: 
                        linetuple2=line.split('\t')
                        x=float(linetuple2[0])
                        y=float(linetuple2[1])
                        z=float(linetuple2[2])
                        self.accelx.append(x)
                        self.accely.append(y)
                        self.accelz.append(z)
                        #print "self.accelx array:"+ str(self.accelx)
                    else:
                        pass
                accelfile.close()
                
                #===============================================================
                # spatialin=[]
                # if plot.p1.trackMotion == True:
                #     for i,accel in spatialin:
                #         accel1=accel.split(',')
                #         x1=float(accel1[0])
                #         y1=float(accel1[1])
                #         z1=float(accel1[2])
                #         self.accelx.append(x1)
                #         self.accely.append(y1)
                #         self.accelz.append(z1)
                #===============================================================
                        
                #need average score for first 10 values for x,y and z. np.mean is a numpy function
                xavg=np.mean(self.accelx [0:9])
                yavg=np.mean(self.accely [0:9])
                zavg=np.mean(self.accelz [0:9])
                #print "x avg:" + str(xavg)
                
                
                # subtract the average values from each read to normalise. normx1 is an array of all x values. this feeds normx which is 
                #populated by these values minus the average. np.array is a numpy function
                normx1=np.array(self.accelx)
                normx=[normx1-xavg]
                normy1=np.array(self.accely)
                normy=[normy1-yavg]
                normz1=np.array(self.accelz)
                normz=[normz1-zavg]                
                #print "self.accelx array:"+ str(normx) 
                
                # turn into velocity (o.5(a(t^2)). uses two values as above.uses freqsq
                velx1=np.array(normx)
                velx=[0.5*(velx1*freqsq)]
                vely1=np.array(normy)
                vely=[0.5*(vely1*freqsq)]
                velz1=np.array(normz)
                velz=[0.5*(velz1*freqsq)]
                
                #print "velocity x:"+str(velx) 
                
                #cumulative velocity. creates an array where each element is the running total of the array (Numpy function)
                cumvelx = np.cumsum(velx)
                cumvely = np.cumsum(vely)
                cumvelz = np.cumsum(velz)
                
                #distance. cumulative velocity times the frequency. timesd by 100,000 to visualise without zooming in.
                disx=cumvelx*freq*100000
                disy=cumvely*freq*100000
                disz=cumvelz*freq*100000
                #print "disx="+str(disx)
                
                #cumulative distance. again uses numpy cumsum function
                cumdisx =np.cumsum(disx)
                cumdisy =np.cumsum(disy)
                cumdisz =np.cumsum(disz)
                #print "cumdisx="+str(cumdisx)
                
                #combine all three arrays (x,Y,Z) back into a single array with each element a tuple of the three arrays 
                #uses zip function
                distancecood= zip(cumdisx,cumdisy,cumdisz)
                print "distancecood="+str(distancecood)
                
                #create a function which will hold points for an updating line
                #self.pointcatcher = linedrawer.linedrawer()
                # iterate through the array adding each element to the linedrawer array
                for i in distancecood:
                    self.pointcatcher.addPoint(i)        
        
        def infile(self,input):
                self.infile = str(input)
                
        def freqin(self,input1):
                self.freqin= float(input1)