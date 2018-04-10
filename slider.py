import vtk


def slider():
    sphereSource = vtk.vtkSphereSource()

    sphereSource.SetCenter(0,0,0)
    sphereSource.SetRadius(4)
    sphereSource.SetPhiResolution(4)
    sphereSource.SetThetaResolution(8)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetInterpolationToFlat()

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor)

    renderWindow.Render()

    sliderRep = vtk.vtkSliderRepresentation3D()
    sliderRep.SetMinimumValue(3.0)
    sliderRep.SetMaximumValue(50.0)
    sliderRep.SetValue(sphereSource.GetThetaResolution())
    sliderRep.SetTitleText("Sphere Resolution")
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToWorld()
    sliderRep.GetPoint1Coordinate().SetValue(-4,6,0)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToWorld()
    sliderRep.GetPoint2Coordinate().SetValue(4, 6, 0)
    sliderRep.SetSliderLength(0.075)
    sliderRep.SetSliderWidth(0.05)
    sliderRep.SetEndCapLength(0.05)

    sliderWidget =  vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(interactor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()
    sliderWidget.EnabledOn()

    interactor.Initialize()
    # renderWindow.Render()
    interactor.Start()

from utils import *
def main():
    pass

main()