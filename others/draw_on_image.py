import vtk

def main():
    img_name = ""
    readerFactory = vtk.vtkImageReader2Factory()
    imgReader  = readerFactory.CreateImageReader2(img_name)
    imgReader.SetFileName(img_name)

    imgReader.Update()

    image = imgReader.GetOutput()

    center = [0,0]
    center[0] = (image.GetExtent()[1] + image.GetExtent()[0])/2
    center[1] = (image.GetExtent()[3] + image.GetExtent()[2])/2

    radius = image.GetExtent()[3]*2/5if image.GetExtent()[1]>image.GetExtent()[3]else image.GetExtent()[1]*2/5

    drawing = vtk.vtkImageCanvasSource2D()

    # draw circle
    drawing.SetNumberOfScalarComponents(3)
    drawing.SetScalarTypeToUnsignedChar()
    drawing.SetExtent(image.GetExent())
    drawing.SetDrawColor(0,0,0)
    drawing.FillBox(image.GetExent()[0],image.GetExent()[1],
                    image.GetExent()[2],image.GetExtent()[3])

    drawing.SetDrawColor(255,255,255)

    drawing.DrawCircle(center[0],center[1],radius)
    # drawing.Draw

drawing = vtk.vtkImageCanvasSource2D()