import vtk
from utils import *
import math


class Widget(object):
    def __init__(self):
        pass


import numpy as np
from actor import *


class BoxWidget(vtk.vtkBoxWidget):
    def __init__(self, renderer, displayer, input=None):
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
        self.init_center = None

    def SetInput(self, input):
        self.input = input

    def ChangeColor(self):
        self.GetOutlineProperty().SetColor([1, 1, 0])

    def UnchangeColor(self):
        self.GetOutlineProperty().SetColor([1, 1, 1])

    def RegisterWidgetCallback(self, displayer):
        from callback import BoxWidgetCallback
        self.box_widget_callback = BoxWidgetCallback(
            self, interactor=displayer.interactor)

    def AdjustColor(self, flag):
        if self.myactor is None:

            self.selection = vtk.vtkExtractGeometry()

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
        print("num of points: ", num_points)
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

    def Generate(self, renderer):
        self.SetInteractor(self.interactor)
        self.SetPlaceFactor(1)
        self.SetDefaultRenderer(renderer)
        # self.GetRepresentation().SetRenderer(renderer)
        self.SetHandleSize(0.001)
        self.RotationEnabledOff()
        self.KeyPressActivationOff()

    def SetCenterAndDim(self, center, dims, angle):
        self.PlaceWidget(*[-0.5, 0.5, -0.5, 0.5, -0.5, 0.5])
        trans = vtk.vtkTransform()
        trans.PostMultiply()
        trans.Identity()
        trans.Scale(dims[2], dims[0], dims[1])
        trans.RotateY(angle)
        self.angle = angle
        trans.Translate(*center)
        self.SetTransform(trans)

    def RegisterCallback(self):
        pass

    def SetMyactor(self, myactor):
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

        l = GetDistanceFromTwoPoints(point_coords[9], point_coords[8])
        h = GetDistanceFromTwoPoints(point_coords[11], point_coords[10])

        w = GetDistanceFromTwoPoints(point_coords[13], point_coords[12])
        if self.orientation in [1, 3]:
            l, w = [w, l]
        center = list(point_coords[-1])
        return center, [h, w, l]

    def SetAngle(self, angle):
        self.angle = angle

    def GetInfo(self):

        center, [h, w, l] = self.GetCenterAndDims()
        center[1] = center[1] + h/2.0
        angle = self.orientation * 90-self.angle
        if angle < 180:
            angle = -angle
        else:
            angle = 360-angle
        return list(map(lambda x: round(x, 2), [h, w, l, center[0], center[1], center[2], angle*math.pi/180]))
