
"""
this file is used for test
"""
from utils import *
from actor import MyActor

from utils import *
from displayer import Displayer
import vtk
from displayer import *
from actor import *
from myio import *
from box_widget import *
import numpy as np

def GetBounds(scans):
    a = np.max(scans,axis=0)
    b = np.min(scans,axis=0)

    print(a)
    print(b)

def slice():
    points_reader = PointCloudReader("../0000000000.bin")

    cutter = vtk.vtkCutter()
    cutter.SetInputConnection(points_reader.GetOutputPort())
    cutPlane = vtk.vtkPlane()
    cutPlane.SetOrigin([0,-10,0])
    cutPlane.SetNormal(0, 1, 0)
    cutter.SetCutFunction(cutPlane)

    points_actor = PolyDataActor(points_reader.GetOutputPort())

    circle_actor = vtk.vtkActor()
    circle_mapper = vtk.vtkPolyDataMapper()
    circle_mapper.SetInputConnection(cutter.GetOutputPort())
    circle_actor.SetMapper(circle_mapper)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.2, 0.4)
    renderer.AddActor(circle_actor)
    # renderer.AddActor(points_actor.actor)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    style = vtk.vtkInteractorStyleImage()
    interactor.SetInteractorStyle(style)
    renderer.ResetCamera()
    interactor.Start()


def main():
    points_reader = PointCloudReader("../0000000000.bin")
    GetBounds(points_reader.scans)
    displayer = StylePickerDisplayer()

    points_actor = PolyDataActor(points_reader.GetOutputPort())

    point_renderer = Renderer([points_actor])

    points = PolyDataStylePickerRenderer(point_renderer)

    displayer.AddStylePickerRenderer(points)
    box = BoxWidget(displayer)
    box.On()
    displayer.Start()


def check_in_line(point1_3D,point2_3D,point3_3D):
    delta1 = point1_3D - point2_3D
    delta2 = point2_3D - point3_3D
    print(delta2,delta1)

def test_null():
    a = transform_matrix3Dto2D()
    b = null(a)
    print(a.dot(b))

def test_transform():

    point_3D = [24.26300048828125, 8.574000358581543, -0.4659999907016754]
    a = np.array(point_3D)
    point_2D = pointtrans3Dto2D(point_3D)

    point_2D = [729,174]
    point_3D_1= pointtrans2Dto3D(point_2D)
    point_3D_2 = pointtrans2Dto3D(point_2D)
    b = np.array(point_3D_1)
    c = np.array(point_3D_2)
    print(b,c)
    check_in_line(a,b,c)

def test_transform_2D():
    point1_2D = [2,4]
    point2_2D = [4,6]
    GetPlaneFromPoint2D(point1_2D,point2_2D)


def test_multiple_windows():
    interactors = []
    for i in range(4):



        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(0,0,0)
        sphereSource.SetRadius(5.0)
        sphereSource.Update()

        myactor = MyActor(sphereSource.GetOutputPort())
        displayer = Displayer(myactor.actor)
        interactors.append(displayer.interactor)
        displayer.window.Render()
        displayer.SetPosition([i*300,0])
        # renderer.AddActor(myactor.actor)
        # renderer.ResetCamera()
    interactors[0].Start()
def test_plane():
    plane = vtk.vtkPlane()
    plane.SetOrigin(0,0,0)
    plane.SetNormal(0,1,-1)
    print(plane.FunctionValue(0,0,1))

from dataset import *
def test_yaml():
    config_parser = ConfigParser()
    config_parser.LoadConfig("./config/example.yaml")
    print(config_parser.GetConfig())
if __name__=="__main__":
    test_yaml()
    # box = vtk.vtkBoxWidget()
    # test_plane()
    # print(transform_matrix3Dto2D())
    # test_transform_2D()
    # test_null()
    # test_transform()
    # main()
    # test_multiple_windows()
    # slice()
