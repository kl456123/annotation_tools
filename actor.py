import vtk
from vtk.util import numpy_support
from utils import *
from abc import ABCMeta,abstractclassmethod


class MyActor(object):
    def __init__(self,polydata):
        super().__init__()
        self.SetMapper()
        self.SetInput(polydata)
        self.SetActor()

        self.actor.SetMapper(self.mapper)

    def GetBounds(self):
        return self.actor.GetBounds()

    def SetInput(self,polydata):

        if isinstance(polydata, vtk.vtkAlgorithmOutput):
            self.mapper.SetInputConnection(polydata)
        elif isinstance(polydata, vtk.vtkDataObject):
            self.mapper.SetInputData(polydata)
        # retrieve data again
        # there may be bug here
        # self.Update()

    def GetPoint(self,pid):
        points_data = self.GetInput()
        return points_data.GetPoint(pid)

    def GetAllPoints(self):
        polydata = self.GetInput()
        return numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())

    def SetScalars(self,scalars):
        self.GetInputAttributes().SetScalars(scalars)

    def GetNumberOfPoints(self):
        return self.GetInput().GetNumberOfPoints()

    def GetNumberOfCells(self):
        return self.GetInput().GetNumberOfCells()

    def GetInput(self):
        return self.mapper.GetInput()

    def GetInputAttributes(self):
        return self.GetInput().GetPointData()

    def GetCenter(self):
        return self.actor.GetCenter()

    def VisibilityOff(self):
        self.actor.VisibilityOff()

    def VisibilityOn(self):
        self.actor.VisibilityOn()

    def Update(self):
        self.mapper.Update()

    def GetScalars(self):
        return self.GetInputAttributes().GetScalars()

    @abstractclassmethod
    def SetMapper(self):
        pass
    @abstractclassmethod
    def SetActor(self):
        pass

class ImageActor(MyActor):

    def SetMapper(self):
        self.mapper = vtk.vtkImageMapper()
        self.SetColorLevel()
        self.SetColorWindow()

    def SetActor(self):
        self.actor = vtk.vtkActor2D()

    def SetColorWindow(self):
        self.mapper.SetColorWindow(255)

    def SetColorLevel(self):
        self.mapper.SetColorLevel(127.5)

class PolyDataActor(MyActor):
    def __init__(self,polydata,dataset=None,colors=None):
        super().__init__(polydata)
        self.polydata = dataset
        self.colors = colors

        self.actor.SetMapper(self.mapper)

    def SetMapper(self):
        self.mapper = vtk.vtkPolyDataMapper()

    # def ColorInsideFrustum(self,box,new=True):
    #     P = GetIntrinsicMatrix()
    #     points = self.GetAllPoints()
    #     mask = get_frustum_points_of_box2d(points,P,box)
    #     if new:
    #         # return a new polydata
    #         selection = points[mask]
    #         return GeneratePointPolyFilter(selection)
    #     else:
    #         # change its attr
    #         self.ColorPointsByMask(mask)

    # def ColorPointsByMask(self,mask,color_name="red"):
    #     # colors = self.GetScalars()
    #     colors = GenerateColors(self.GetNumberOfPoints(), color_name=color_name)
    #     # colors = self.colors
    #     ids = np.where(mask)[0]
    #     for i in ids:
    #         colors.SetTypedTuple(i,[0, 255, 0])
    #     self.SetScalars(colors)
        # self.polydata.Modified()
        # self.Update()

    def SetActor(self):
        self.actor = vtk.vtkActor()
