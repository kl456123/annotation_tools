import vtk
import numpy as np
import math

from annotation_tools.core.actor import PolyDataActor
from annotation_tools.callbacks.box_widget_callback import BoxWidgetCallback
from annotation_tools.utils.common_util import color_map, GenerateColors
from annotation_tools.utils.geometry_util import GetDistanceFromTwoPoints, GetBoundsCenter


class Widget(object):
    def __init__(self):
        pass


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
        self.velo_only = displayer.velo_only
        self.color = [1, 1, 1]

        self.RegisterWidgetCallback(displayer)

    def SetColor(self, color):
        self.color = color
        self.UnchangeColor()

    # def SetColorByClass(self, class_idx, classes_colors_map):
        # self.color = color_map(classes_colors_map[class_idx])
        # self.UnchangeColor()

    def SetInput(self, input):
        self.input = input

    def ChangeColor(self):
        self.GetOutlineProperty().SetColor([1, 1, 0])

    def UnchangeColor(self):
        self.GetOutlineProperty().SetColor(self.color)

    def RegisterWidgetCallback(self, displayer):
        self.box_widget_callback = BoxWidgetCallback(self, displayer)

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

        f = self.GetEnabled() if flag else not self.GetEnabled()
        if f:
            color_name = "green"
        else:
            color_name = "red"
        # generate colors
        selected_colors = GenerateColors(num_points, color_name=color_name)

        # set attribution of points
        self.myactor.SetScalars(selected_colors)

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
        # if self.velo_only:
        #     trans.RotateZ(angle)
        # else:
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
        # if self.velo_only:
        #     center[2] = center[2]-h/2.0
        # else:
        center[1] = center[1] + h / 2.0
        angle = self.orientation * 90 - self.angle
        if angle < 180:
            angle = -angle
        else:
            angle = 360 - angle
        return list(
            map(lambda x: round(x, 2), [
                h, w, l, center[0], center[1], center[2], angle * math.pi / 180
            ]))
