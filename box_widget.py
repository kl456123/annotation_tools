import vtk
from utils import GetBoundsCenter

class Widget(object):
    def __init__(self):
        pass

class BoxWidget(vtk.vtkBoxWidget):
    def __init__(self,renderer,displayer):
        super().__init__()
        self.interactor = displayer.interactor
        # renderer = renderer
        self.Generate(renderer)
        self.angle = 0
        self.myactor = None

    def Generate(self,renderer):
        self.SetInteractor(self.interactor)
        self.SetPlaceFactor(1)
        self.SetCurrentRenderer(renderer)
        # self.GetRepresentation().SetRenderer(renderer)
        self.SetHandleSize(0.001)


    def RegisterCallback(self):
        pass

    def SetMyactor(self,myactor):
        self.myactor = myactor
        self.PlaceWidget(self.myactor.GetBounds())

    def GetCenter(self):
        return GetBoundsCenter(self.GetBounds())

    def GetBounds(self):
        return self.myactor.GetBounds()

    def SetAngle(self,angle):
        self.angle = angle

    def GetInfo(self):
        center = self.GetCenter()
        xmin, xmax, ymin, ymax, zmin, zmax = self.GetBounds()
        x_dim = xmax-xmin
        y_dim = ymax-ymin
        z_dim = zmax-zmin
        return [x_dim,y_dim,z_dim,*center,self.angle]

class BorderWidget(vtk.vtkBorderWidget):
    def __init__(self,start,end,img_start,interactor):
        super().__init__()
        self.coords = []
        self.interactor = interactor
        self.img_start = img_start
        self.SetInteractor(self.interactor)
        self.Generate(start,end)

        # leftbottom righttop


    def GetInfo(self,img_size):
        self.coords[1]=img_size[1] - self.coords[1]
        self.coords[3] = img_size[1]-self.coords[3]
        return self.coords

    def SetRenderer(self,renderer):
        self.GetBorderRepresentation().SetRenderer(renderer)

    def Generate(self,start,end):
        new_original = []
        size = list(self.interactor.GetRenderWindow().GetSize())
        new_original.append(self.img_start[0] * size[0])
        new_original.append(self.img_start[1] * size[1])

        new_start = [start[0],end[1]-new_original[1]]
        new_end = [end[0],start[1]-new_original[1]]

        self.coords+=new_start
        self.coords+=new_end

        print("start,end: ",start,end)
        print("new_start,new_end: ",new_start, new_end)
        size[1] -= new_original[1]
        tmp = [new_start[0] / size[0], new_start[1] / size[1]]

        print("scaled bottom_left: ",tmp)
        print("scaled top_right: ",new_end[0]/size[0],new_end[1]/size[1])
        representation = vtk.vtkBorderRepresentation()
        # representation

        representation.SetPosition(tmp[0],tmp[1])
        representation.SetPosition2(new_end[0]/size[0]-tmp[0],new_end[1]/size[1]-tmp[1])
        self.SetRepresentation(representation)
        self.SetInteractor(self.interactor)
        self.SelectableOff()
        # self.SetEnabled(1)
        # print(self.GetEnabled())
        # self.ProcessEventsOff()
        self.SetProcessEvents(False)
        self.ResizableOff()
        self.On()


