from actor import *
from myio import *
from displayer import *

def test_imgactor():
    img_reader = ImageReaderFactory().GenerateImageReader("./data/0000000000.png")

    img_actor = ImageActor(img_reader.GetOutputPort())

    renderer = Renderer([img_actor])

    displayer = Displayer()

    displayer.AddRenderer(renderer)
    displayer.Start()

def test_polydata():
    points_reader = PointCloudReader("../0000000000.bin")

    points_actor = PolyDataActor(points_reader.GetOutputPort())

    renderer = Renderer([points_actor])

    style = vtk.vtkInteractorStyleRubberBandPick()

    picker = vtk.vtkAreaPicker()

    # Displayer
    displayer = Displayer()

    displayer.AddRenderer(renderer)

    displayer.Start()

def main():
    # all pass
    test_imgactor()
    test_polydata()


main()
