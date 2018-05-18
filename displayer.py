import vtk
from actor import MyActor
from callback import *
from box_widget import BoxWidget
from border_widget import BorderWidget





class Displayer(object):
    def __init__(self):

        self.SetWindow()

        self.SetInteractor()

        self.RegisterDisplayerCallback()

    def AddRenderer(self, renderer):
        if renderer:
            self.window.AddRenderer(renderer)

    def SetWindow(self):
        self.window = vtk.vtkRenderWindow()

        # self.window.SetFullScreen()

    def SetDataSet(self, dataset):
        self.dataset = dataset

    def SetInteractor(self):
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

    def Render(self):
        self.window.Render()

    def Start(self):
        self.interactor.Initialize()
        self.interactor.Start()

    def RegisterDisplayerCallback(self):
        pass


from selection import *



