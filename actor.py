import vtk
from vtk.util import numpy_support
from utils import *
from abc import ABCMeta,abstractclassmethod


class MyActor(object):
    def __init__(self,polydata):
        super().__init__()
        self.mapper = None
        self.actor = None
        self.SetMapper()
        self.SetInput(polydata)
        self.SetActor()

        self.actor.SetMapper(self.mapper)

    def GetBounds(self):
        return self.actor.GetBounds()

    def SetInput(self,polydata):

        if isinstance(polydata, vtk.vtkAlgorithm):
            self.mapper.SetInputConnection(polydata.GetOutputPort())
        elif isinstance(polydata,vtk.vtkAlgorithmOutput):
            self.mapper.SetInputConnection(polydata)
        elif isinstance(polydata, vtk.vtkDataObject):
            self.mapper.SetInputData(polydata)

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
    def __init__(self,polydata):
        super().__init__(polydata)

        self.actor.SetMapper(self.mapper)

    def SetMapper(self):
        self.mapper = vtk.vtkPolyDataMapper()

    def SetActor(self):
        self.actor = vtk.vtkActor()
