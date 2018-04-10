import vtk
import math
from myio import *

def main():
    points_reader = PointCloudReader("../0000000000.bin")

    sphereSource = vtk.vtkSphereSource()

    sphereSource.SetPhiResolution(30)
    sphereSource.SetThetaResolution(30)
    sphereSource.SetCenter(40,40,0)
    sphereSource.SetRadius(20)

    circleCutter = vtk.vtkCutter()
    circleCutter.SetInputConnection(points_reader.GetOutputPort())

    cutPlane = vtk.vtkPlane()
    cutPlane.SetOrigin([0,0,0])
    # cutPlane.SetOrigin(sphereSource.GetCenter())
    cutPlane.SetNormal(0,0,1)

    circleCutter.SetCutFunction(cutPlane)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(circleCutter.GetOutputPort())
    stripper.Update()

    circle = stripper.GetOutput()
    circle_actor = vtk.vtkActor()
    circle_mapper = vtk.vtkPolyDataMapper()
    circle_mapper.SetInputConnection(circleCutter.GetOutputPort())
    circle_actor.SetMapper(circle_mapper)

    polyDataWriter = vtk.vtkXMLPolyDataWriter()
    polyDataWriter.SetInputData(circle)
    polyDataWriter.SetFileName("circle.vtp")
    polyDataWriter.SetCompressorTypeToNone()
    polyDataWriter.SetDataModeToAscii()
    polyDataWriter.Write()

    whiteImage = vtk.vtkImageData()
    bounds = circle.GetBounds()
    spacing=[0.5,0.5,0.5]
    whiteImage.SetSpacing(spacing)

    dim = [0,0,0]
    for i in range(3):
        dim[i] = math.ceil((bounds[i*2+1]-bounds[i*2])/spacing[i])+1

    whiteImage.SetDimensions(dim)
    whiteImage.SetExtent(0,dim[0]-1,0,dim[1]-1,0,dim[2]-1)

    origin = [bounds[0],bounds[1],bounds[2]]
    whiteImage.SetOrigin(origin)
    whiteImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)

    inval = 255
    outval = 0

    count = whiteImage.GetNumberOfPoints()

    for i in range(count):
        scalars = whiteImage.GetPointData().GetScalars()
        # f = vtk.vtkFloatArray()
        # f.SetV
        scalars.SetValue(i,inval)

    extruder = vtk.vtkLinearExtrusionFilter()
    extruder.SetInputData(circle)
    extruder.SetScaleFactor(1.)
    extruder.SetVector(0,0,1)
    extruder.Update()

    pol2stenc = vtk.vtkPolyDataToImageStencil()
    pol2stenc.SetTolerance(0)
    pol2stenc.SetInputConnection(extruder.GetOutputPort())
    pol2stenc.SetOutputOrigin(origin)
    pol2stenc.SetOutputSpacing(spacing)
    pol2stenc.SetOutputWholeExtent(whiteImage.GetExtent())
    pol2stenc.Update()

    imgstenc = vtk.vtkImageStencil()
    imgstenc.SetInputData(whiteImage)
    imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())

    imgstenc.ReverseStencilOff()
    imgstenc.SetBackgroundValue(outval)
    imgstenc.Update()

    # mapper = vtk.vtkImageMapper()
    # mapper.SetInputConnection(imgstenc.GetOutputPort())
    imgactor = vtk.vtkImageActor()
    imgactor.GetMapper().SetInputConnection(imgstenc.GetOutputPort())

    renderer = vtk.vtkRenderer()

    renderer.SetBackground(0.1,0.2,0.4)
    renderer.AddActor(imgactor)
    renderer.AddActor(circle_actor)
    # renderer.AddActor(actor)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    style = vtk.vtkInteractorStyleImage()
    interactor.SetInteractorStyle(style)
    renderer.ResetCamera()
    interactor.Start()

    imageWriter = vtk.vtkMetaImageWriter()
    imageWriter.SetFileName("labelImage.mhd")
    imageWriter.SetInputConnection(imgstenc.GetOutputPort())
    imageWriter.Write()

main()