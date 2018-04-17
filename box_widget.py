import vtk
from utils import *
import math
class Widget(object):
    def __init__(self):
        pass
import numpy as np


class BoxWidget(vtk.vtkBoxWidget):
    def __init__(self,renderer,displayer):
        super().__init__()
        self.interactor = displayer.interactor
        # renderer = renderer
        self.Generate(renderer)
        self.angle = 0
        self.myactor = None
        self.orientation = 0


    # def Rotate(self,angle):


    def Generate(self,renderer):
        self.SetInteractor(self.interactor)
        self.SetPlaceFactor(1)
        self.SetCurrentRenderer(renderer)
        # self.GetRepresentation().SetRenderer(renderer)
        self.SetHandleSize(0.001)

    def SetCenterAndDim(self,center,dims,angle):
        self.PlaceWidget(*[-0.5,0.5,-0.5,0.5,-0.5,0.5])
        trans = vtk.vtkTransform()
        trans.PostMultiply()
        trans.Identity()
        trans.Scale(dims[2],dims[0],dims[1])
        trans.RotateY(angle)
        trans.Translate(*center)
        self.SetTransform(trans)

    def RegisterCallback(self):
        pass

    def SetMyactor(self,myactor):
        self.myactor = myactor
        # trans = vtk.vtkTransform()
        # trans.Scale()
        self.PlaceWidget(self.myactor.GetBounds())

    def GetCenter(self):
        return GetBoundsCenter(self.GetBounds())

    def GetBounds(self):
        polydata = vtk.vtkPolyData()
        self.GetPolyData(polydata)
        return polydata.GetBounds()

    def GetCenterAndDims(self):
        poly = vtk.vtkPolyData()
        self.GetPolyData(poly)
        point_coords = []
        for i in range(poly.GetNumberOfPoints()):
            p = [0, 0, 0]
            poly.GetPoint(i, p)
            point_coords.append(p)
        point_coords = np.array(point_coords)

        l =  GetDistanceFromTwoPoints(point_coords[9],point_coords[8])
        h =GetDistanceFromTwoPoints(point_coords[11],point_coords[10])

        w = GetDistanceFromTwoPoints(point_coords[13] , point_coords[12])
        if self.orientation in [1,3]:
            l,w = [w,l]
        center = list(point_coords[-1])
        return center,[h,w,l]

    def SetAngle(self,angle):
        self.angle = angle

    def GetInfo(self):

        center ,[h,w,l] = self.GetCenterAndDims()
        center[1] =center[1]+ h/2.0
        angle = self.angle + self.orientation * 90
        if angle<180:
            angle = -angle
        else:
            angle = 360-angle
        return list(map(lambda x:round(x,2),[h,w,l,*center,angle*math.pi/180]))

class BorderWidget(vtk.vtkBorderWidget):
    def __init__(self,start,end,img_start,interactor):
        super().__init__()
        self.coords = []
        self.interactor = interactor
        self.img_start = img_start
        self.SetInteractor(self.interactor)
        self.Generate(start,end)

        # leftbottom righttop


    def GetInfo(self,img_size):
        # note here fix bug
        a,b = self.coords[1],self.coords[3]
        self.coords[1]=img_size[1] - b
        self.coords[3] = img_size[1]-a
        return list(map(lambda x:round(x,2),self.coords))

    def SetRenderer(self,renderer):
        self.GetBorderRepresentation().SetRenderer(renderer)

    def Generate(self,start,end):
        new_original = []
        size = list(self.interactor.GetRenderWindow().GetSize())
        new_original.append(self.img_start[0] * size[0])
        new_original.append(self.img_start[1] * size[1])

        new_start = [start[0],end[1]-new_original[1]]
        new_end = [end[0],start[1]-new_original[1]]

        self.coords+=new_start
        self.coords+=new_end

        print("start,end: ",start,end)
        print("new_start,new_end: ",new_start, new_end)
        size[1] -= new_original[1]
        tmp = [new_start[0] / size[0], new_start[1] / size[1]]

        print("scaled bottom_left: ",tmp)
        print("scaled top_right: ",new_end[0]/size[0],new_end[1]/size[1])
        representation = vtk.vtkBorderRepresentation()
        # representation

        representation.SetPosition(tmp[0],tmp[1])
        representation.SetPosition2(new_end[0]/size[0]-tmp[0],new_end[1]/size[1]-tmp[1])
        self.SetRepresentation(representation)
        self.SetInteractor(self.interactor)
        self.SelectableOff()
        self.ProcessEventsOff()
        self.ResizableOff()
        self.On()



