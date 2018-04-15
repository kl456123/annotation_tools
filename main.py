from displayer import *
from selection import Selection
from actor import *
from myio import *
from dataset import *
def main():
    # some config
    img_view_port = [0, 0.5, 1.0, 1.0]
    poly_view_port = [0,0,1.0,0.5]

    img_bg = [0.1, 0.2, 0.4]
    root_path = "./kitti"
    dataset = Dataset(root_path)

    # Displayer
    displayer = StylePickerDisplayer()
    displayer.SetDataSet(dataset)

    # points
    # points_reader = PointCloudReader()
    # points_reader.SetFileName("../0000000000.bin")
    # dataset.pc_reader.SetFileName("./kitti/velodyne_points/data/0000000000.bin")

    points_actor = PolyDataActor(dataset.pc_reader.GetOutputPort())

    # renderer
    point_renderer = Renderer([points_actor])

    selection = Selection(dataset.pc_reader.vertexGlyphFilter ,
                          renderer=point_renderer,
                          displayer=displayer,
                          point_renderer=point_renderer,
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

    # img_reader = ImageReaderFactory().GenerateImageReader("png")
    # dataset.img_reader.SetFileName("./kitti/image_00/data/0000000000.png")
    img_actor = ImageActor(dataset.img_reader.GetOutputPort())
    img_renderer.AddMyActor(img_actor)



    img = ImageStylePickerRenderer(img_renderer,selection, myactor=points_actor)
    img.RegisterStyleCallback(displayer,[img_view_port[0],img_view_port[1]])

    displayer.AddStylePickerRenderer(img)

    displayer.SetPointActor(points_actor)
    displayer.SetImageActor(img_actor)


    displayer.Start()

main()