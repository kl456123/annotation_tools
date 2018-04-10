from displayer import *
from selection import Selection
from actor import *
from myio import *

def main():
    # some config
    img_view_port = [0, 0.5, 1.0, 1.0]
    poly_view_port = [0,0,1.0,0.5]

    img_bg = [0.1, 0.2, 0.4]

    # Displayer
    displayer = StylePickerDisplayer()

    # points
    points_reader = PointCloudReader("../0000000000.bin")

    points_actor = PolyDataActor(points_reader.GetOutputPort())

    # renderer
    point_renderer = Renderer([points_actor])

    selection = Selection(points_reader.vertexGlyphFilter ,
                          renderer=point_renderer,
                          displayer=displayer,
                          debug=False)


    displayer.SetSelection(selection)

    point_renderer.SetViewport(poly_view_port)

    selection.SetRenderer(point_renderer)


    point_renderer.RegisterCameraCallback(displayer)

    points = PolyDataStylePickerRenderer(point_renderer,selection)
    points.RegisterPickerCallback(displayer)

    displayer.AddStylePickerRenderer(points)

    displayer.SetFileName("demo.pkl")


    # img
    img_renderer = Renderer()
    img_renderer.SetBackground(*img_bg)
    img_renderer.SetViewport(*img_view_port)

    img_reader = ImageReaderFactory().GenerateImageReader("./data/0000000000.png")
    img_actor = ImageActor(img_reader.GetOutputPort())
    img_renderer.AddMyActor(img_actor)



    img = ImageStylePickerRenderer(img_renderer,selection, myactor=points_actor)
    img.RegisterStyleCallback(displayer,[img_view_port[0],img_view_port[1]])

    displayer.AddStylePickerRenderer(img)


    displayer.Start()

main()