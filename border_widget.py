import vtk

widgets = []





from myio import *
from actor import *


def main():
    img_reader = ImageReaderFactory().GenerateImageReader("png")
    img_reader.SetFileName("./kitti/image_00/000000.png")
    img_actor = ImageActor(img_reader.GetOutputPort())

    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(4.0)
    sphereSource.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()

    renderWindow.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    # borderWidget = vtk.vtkBorderWidget()
    # borderWidget.SetInteractor(interactor)
    #
    # representation = vtk.vtkBorderRepresentation()
    # representation.SetPosition(0, 0)
    # representation.SetPosition2(0.1, 0.1)
    # borderWidget.SetRepresentation(representation)


    # borderWidget.CreateDefaultRepresentation()
    # borderWidget.SelectableOff()

    style = vtk.vtkInteractorStyleRubberBand2D()

    def gen(style, event):
        size = renderWindow.GetSize()
        start = list(style.GetStartPosition())
        end = list(style.GetEndPosition())
        new_start = [start[0], end[1]]
        new_end = [end[0], start[1]]
        print("start,end: ", start, end)
        print("new_start,new_end: ", new_start, new_end)
        tmp = [new_start[0] / size[0], new_start[1] / size[1]]

        print("scaled bottom_left: ", tmp)
        print("scaled top_right: ", new_end[0] / size[0], new_end[1] / size[1])
        representation = vtk.vtkBorderRepresentation()
        borderWidget = vtk.vtkBorderWidget()

        representation.SetPosition(tmp[0], tmp[1])
        representation.SetPosition2(new_end[0] / size[0] - tmp[0], new_end[1] / size[1] - tmp[1])

        representation.SetMoving(0)
        print("Moving status: ",representation.GetMoving())
        borderWidget.SetRepresentation(representation)
        borderWidget.SetInteractor(interactor)
        borderWidget.ResizableOn()
        # borderWidget.CreateDefaultRepresentation()
        # borderWidget.SelectableO()
        borderWidget.On()
        renderWindow.Render()
        widgets.append(borderWidget)

    def stylecallback(style, event):
        size = renderWindow.GetSize()
        start = list(style.GetStartPosition())
        end = list(style.GetEndPosition())
        new_start = [start[0], end[1]]
        new_end = [end[0], start[1]]
        print("start,end: ", start, end)
        print("new_start,new_end: ", new_start, new_end)
        tmp = [new_start[0] / size[0], new_start[1] / size[1]]

        print("scaled bottom_left: ", tmp)
        print("scaled top_right: ", new_end[0] / size[0], new_end[1] / size[1])
        representation = vtk.vtkBorderRepresentation()
        borderWidget = vtk.vtkBorderWidget()
        # representation.ResizableOff()
        # representation = vtk.vtkBorderRepresentation()
        # representation

        representation.SetPosition(tmp[0], tmp[1])
        representation.SetPosition2(new_end[0] / size[0] - tmp[0], new_end[1] / size[1] - tmp[1])
        # new_start = [start[0],end[1]]
        # new_end = [end[0],start[1]]
        # print(start,end)
        # print(new_start, new_end)
        # print(new_start[0]/size[0],new_start[1]/size[1])
        # print(new_end[0]/size[0],new_end[1]/size[1])

        # # representation
        # tmp = [new_start[0]/size[0],new_start[1]/size[1]]
        # representation.SetPosition(tmp[0],tmp[1])
        # representation.SetPosition2(new_end[0]/size[0]-tmp[0],new_end[1]/size[1]-tmp[1])
        representation.SetMoving(0)
        print("Moving status: ",representation.GetMoving())
        borderWidget.SetRepresentation(representation)
        borderWidget.SetInteractor(interactor)
        borderWidget.ResizableOn()
        # borderWidget.CreateDefaultRepresentation()
        # borderWidget.SelectableO()
        borderWidget.On()
        renderWindow.Render()
        widgets.append(borderWidget)

    # style.AddObserver("SelectionChangedEvent",stylecallback)
    interactor.SetInteractorStyle(style)
    renderer.AddActor(actor)
    renderer.AddActor(img_actor.actor)

    interactor.Initialize()
    renderWindow.Render()
    # borderWidget.On()

    interactor.Start()

main()