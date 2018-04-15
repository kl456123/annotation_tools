from displayer import Displayer
from myio import *
from mystyle import *
from actor import *

def create_color_image(image):
    dim = 20
    image.SetDimensions(dim,dim,1)
    image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,3)
    for x in range(dim):
        for y in range(dim):
            # pixel=[0,0,0,0]
            # pixel = image.GetScalarPointer(x,y,0)
            # pixel = image.GetScalarComponentAsDouble(x,y,0)
            if x<dim/2:
                image.SetScalarComponentFromFloat(x,y,0,0,255)
                image.SetScalarComponentFromFloat(x,y,0,1,0)
                # pixel[0]=255
                # pixel[1]=0
            else:
                image.SetScalarComponentFromFloat(x,y,0,0,0)
                image.SetScalarComponentFromFloat(x,y,0,1,255)
            image.SetScalarComponentFromFloat(x, y, 0, 2, 0)
    image.Modified()

def GetImageActor(img_name):
    img_reader = ImageReaderFactory().GenerateImageReader(img_name)


    image_mapper = vtk.vtkImageMapper()

    image_mapper.SetInputConnection(img_reader.GetOutputPort())

    image_mapper.SetColorWindow(255)
    image_mapper.SetColorLevel(127.5)

    imageActor = vtk.vtkActor2D()

    imageActor.SetMapper(image_mapper)

    return imageActor



def main():
    img_reader = ImageReaderFactory().GenerateImageReader("./data/0000000000.png")

    img_actor = ImageActor(img_reader.GetOutputPort())

    displayer = Displayer(img_actor.actor)

    displayer.Start()


if __name__=="__main__":
    main()