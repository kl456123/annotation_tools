import vtk
from utils import *
import math
class Widget(object):
    def __init__(self):
        pass
import numpy as np
from actor import *
# from callback import BoxWidgetCallback

class BoxWidget(vtk.vtkBoxWidget):
    def __init__(self,renderer,displayer,input=None):
        super().__init__()
        self.interactor = displayer.interactor
        self.renderer = renderer
        self.Generate(renderer)
        self.angle = 0
        self.myactor = None
        self.orientation = 0
        self.SetInput(input)
        self.selected = False
        self.selection = None

    def SetInput(self,input):
        self.input = input

    def RegisterWidgetCallback(self,displayer):
        self.box_widget_callback = BoxWidgetCallback(self,interactor=displayer.interactor)

    def AdjustColor(self,flag):
        if self.myactor is None:

            # selectEnclosedPoints.Update()

            self.selection = vtk.vtkExtractGeometry()
            # self.selection.SetSurfaceConnection(polydata)
            # self.selection.SetImplicitFunction(func)
            self.selection.SetInputConnection(self.input.GetOutputPort())
            filter = vtk.vtkVertexGlyphFilter()
            filter.SetInputConnection(self.selection.GetOutputPort())
            self.myactor = PolyDataActor(filter.GetOutputPort())
            self.renderer.AddMyActor(self.myactor)

        polydata = vtk.vtkPolyData()
        self.GetPolyData(polydata)
        self.selection.SetImplicitFunction(polydata)
        self.myactor.Update()
        num_points = self.myactor.GetNumberOfPoints()
        print("num of points: ",num_points)
        num_cells = self.myactor.GetNumberOfCells()

        f = self.GetEnabled() if flag else not self.GetEnabled()
        if f:
            color_name = "green"
        else:
            color_name = "red"
        # generate colors
        selected_colors = GenerateColors(num_points, color_name=color_name)

        # set attribution of points
        self.myactor.SetScalars(selected_colors)



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
        self.angle = angle
        trans.Translate(*center)
        self.SetTransform(trans)

    def RegisterCallback(self):
        pass

    def SetMyactor(self,myactor):
        self.selected = True
        self.init_center = myactor.GetCenter()
        self.PlaceWidget(myactor.GetBounds())

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
        angle =   self.orientation * 90-self.angle
        if angle<180:
            angle = -angle
        else:
            angle = 360-angle
        return list(map(lambda x:round(x,2),[h,w,l,center[0],center[1],center[2],angle*math.pi/180]))

class BorderWidget(vtk.vtkBorderWidget):
    def __init__(self,start,end,img_start,renderer,interactor):
        super().__init__()
        self.coords = []
        self.SetRenderer(renderer)
        self.interactor = interactor
        self.img_start = img_start
        self.SetInteractor(self.interactor)
        self.Generate(start,end)


    def GetInfo(self,img_size):
        rep = self.GetBorderRepresentation()

        pos = np.array(rep.GetPosition())
        pos2 = np.array(rep.GetPosition2())

        pos2+=pos

        # normalized coordinates
        box = np.concatenate([pos,pos2])

        size = list(self.interactor.GetRenderWindow().GetSize())

        # view_port size
        size[1] -=self.img_start[1] * size[1]

        # original coordinates

        # box left bottom and right top
        box[::2]*=size[0]
        box[1::2]*=size[1]

        # box left top and right bottom
        a,b = box[1],box[3]

        box[1] = img_size[1] - b
        box[3] = img_size[1] - a

        res1 = list(map(lambda x: round(x, 2), list(box)))

        return res1

    def SetRenderer(self,renderer):
        self.SetCurrentRenderer(renderer)

    def Generate(self,start,end):
        new_original = []
        size = list(self.interactor.GetRenderWindow().GetSize())
        new_original.append(self.img_start[0] * size[0])
        new_original.append(self.img_start[1] * size[1])

        new_start = [start[0],end[1]-new_original[1]]
        new_end = [end[0],start[1]-new_original[1]]

        self.coords+=new_start
        self.coords+=new_end

        size[1] -= new_original[1]
        tmp = [new_start[0] / size[0], new_start[1] / size[1]]

        representation = vtk.vtkBorderRepresentation()
        # representation

        representation.SetPosition(tmp[0],tmp[1])
        representation.SetPosition2(new_end[0]/size[0]-tmp[0],new_end[1]/size[1]-tmp[1])
        # representation.MovingOff()
        self.SetRepresentation(representation)
        self.SetInteractor(self.interactor)
        # self.SelectableOff()

        # self.ProcessEventsOff()
        self.ResizableOn()
        # print("resize: ",self.GetResizable())
        self.On()



