# -*- coding: utf-8 -*-


import vtk
from annotation_tools.callback import Callback

class BoxWidgetCallback(Callback):
    def __init__(self, obj, displayer, debug=False):
        super().__init__(obj, debug, displayer.interactor)
        self.displayer = displayer

    # def UpdateSurface(self, obj, event):
    #     if self.obj.selection is None:
    #         return
    #     polydata = vtk.vtkPolyData()
    #     obj.GetPolyData(polydata)
    #     self.obj.selection.SetSurfaceData(polydata)
    #     self.obj.selection.Update()

    def SelectedEvent(self, obj, event):
        print("box widget is selected! ")

        self.displayer.pc_style_picker.SetCurrentBoxWidget(self.obj)

        self.displayer.Render()

    def Start(self):
        self.AddEventObserver(vtk.vtkCommand.StartInteractionEvent,
                              self.SelectedEvent)
        # self.AddEventObserver("InteractionEvent", self.UpdateSurface)


