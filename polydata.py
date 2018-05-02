import vtk

#
# class PolyData(vtk.vtkPolyData):
#     def __init__(self):
#         super().__init__()
#
#     def GenerateQuad(self,point_coords):
#         pass
#
#     def GeneratePoints(self):
#         pass
#
#     def GenerateCells(self):
#         pass

# class Builder(object):
#     def __init__(self,point_coords):
#         self.polydata = vtk.vtkPolyData()
#         self.points = vtk.vtkPoints()
#         self.cells = vtk.vtkCellArray()
#         self.polydata.SetLines(self.cells)
#         self.polydata.SetPoints(self.points)
#         self.point_coords = point_coords
#
#     def BuildPoints(self):
#         pass
#     def BuildCells(self):
#         pass
#
# class Director(object):
#     def __init__(self):
#         pass
#     def SetInput(self,point_coords):
#         self.point_coords = point_coords
#
#     def BuildQuad(self,builder):
#         builder.BuildPoints()
#         builder.BuildCells()
#
# class QuadBuilder(Builder):
#     # def __init__(self):
#     #     super().__init__()
#
#     def BuildCells(self):
#         self.num_cells = self.num_points+1
#         self.cells.InsertNextCell(self.num_cells)
#         for i in range(self.num_cells):
#             self.cells.InsertCellPoint(i)
#
#         # enclose
#         self.cells.InsertCellPoint(0)
#
#     def BuildPoints(self):
#         self.num_points = len(self.point_coords)
#         for point_coord in self.point_coords:
#             self.points.SetPoint(*point_coord)


# abstract factory method


class AbstractFactory(object):
    def __init__(self):
        pass
        # self.polydata = vtk.vtkPolyData()
        # self.points = vtk.vtkPoints()
        # self.cells = vtk.vtkCellArray()
        # self.polydata.SetLines(self.cells)
        # self.polydata.SetPoints(self.points)
        # self.point_coords = point_coords
        # self.num_points = len(self.point_coords)

    def CreateDataset(self):
        pass

    def CreatePoints(self,point_coords):
        pass

    def CreateCells(self,pts):
        pass

    def CreateIdList(self):
        pass

class QuadFactory(AbstractFactory):

    def CreateIdList(self):
        return [(0,1),(1,2),(2,3),(3,0)]

    def CreateDataset(self):
        return vtk.vtkPolyData()

    def CreateCells(self,pts):
        # pts = [(0,1),(1,2),(2,3),(3,0)]
        cells = vtk.vtkCellArray()
        for i in range(len(pts)):
            cells.InsertNextCell(mkVtkIdList(pts[i]))
        return cells

    def CreatePoints(self,point_coords):
        points = vtk.vtkPoints()
        num_points = len(point_coords)
        points.SetNumberOfPoints(num_points)

        for idx,point_coord in enumerate(point_coords):
            points.SetPoint(idx,point_coord)

        return points







class Builder(object):
    def __init__(self):
        pass

    def CreatePolyData(self,factory,point_coords):
        polydata = factory.CreateDataset()
        points = factory.CreatePoints(point_coords)
        pts = factory.CreateIdList()
        cells = factory.CreateCells(pts)
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        return polydata



from actor import *
from displayer import *
import math
from utils import CreateBoxCoordsFromCorner
from myio import *
def main():
    # c = math.cos(math.pi / 6)
    img_reader = ImageReaderFactory().GenerateImageReader("./data/0000000000.png")
    img_actor = ImageActor(img_reader.GetOutputPort())

    point_coords = CreateBoxCoordsFromCorner([0,0,0],[2,2,0])

    quad = QuadFactory()
    build = Builder()
    polydata = build.CreatePolyData(quad,point_coords)

    polygonMapper = vtk.vtkPolyDataMapper()
    polygonMapper.SetInputData(polydata)

    polygonActor = vtk.vtkActor()
    polygonActor.SetMapper(polygonMapper)

    ren1 = vtk.vtkRenderer()
    ren1.AddActor(img_actor.actor)
    ren1.AddActor(polygonActor)
    # ren1.SetBackground(0.1, 0.2, 0.4)
    # vtk.vtkImageCa
    ren1.ResetCamera()

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(300, 300)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.Initialize()
    iren.Start()

main()