import vtk
import math
from myio import *
from actor import *

def main():
    img_reader = ImageReaderFactory().GenerateImageReader("./data/0000000000.png")

    img_actor = ImageActor(img_reader.GetOutputPort())

    contour_widget = vtk.vtkContourWidget()

    contourRepresentation = vtk.vtkOrientedGlyphContourRepresentation()
    contourRepresentation.GetLinesProperty().SetColor(1,1,0)

    contour_widget.SetRepresentation(contourRepresentation)
    contour_widget.GetContourRepresentation().SetLineInterpolator(vtk.vtkLinearContourLineInterpolator())

    numPts = 10

    points = vtk.vtkPoints()

    for i in range(numPts):
        angle = 2.0*vtk.vtkMath.Pi()*i/numPts
        points.InsertNextPoint([0.1*math.cos(angle),0.1*math.sin(angle),-1.0])

    vertexIndices = vtk.vtkIdList()
    for i in range(numPts):
        vertexIndices.InsertNextId(i)
    # vertexIndices.InsertNextId(0)

    lines = vtk.vtkCellArray()
    lines.InsertNextCell(vertexIndices)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)

    mapper = vtk.vtkPolyDataMapper2D()
    mapper.SetInputData(polydata)
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1,0.2,0.4)
    renderer.AddActor(img_actor.actor)
    renderer.AddActor(actor)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    style = vtk.vtkInteractorStyleJoystickCamera()
    interactor.SetInteractorStyle(style)

    contour_widget.SetInteractor(interactor)
    contour_widget.On()
    contour_widget.Initialize(polydata)
    renderer.ResetCamera()
    interactor.Start()

main()



