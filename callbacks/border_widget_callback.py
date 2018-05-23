# -*- coding: utf-8 -*-

from annotation_tools.callback import Callback
import vtk

class BorderWidgetCallback(Callback):
    def __init__(self, obj, displayer, debug=False):
        super().__init__(obj, debug, displayer.interactor)
        self.displayer = displayer

    def Start(self):
        self.AddEventObserver(vtk.vtkCommand.StartInteractionEvent,
                              self.SelectedEvent)

    def SelectedEvent(self, obj, event):
        print("border widget is selected! ")

        # set border widget for image renderer style
        self.displayer.img_style_picker.SetCurrentBorderWidget(self.obj)

        # self.obj.ChangeColor()

        # set box widget for pc renderer style
        self.displayer.pc_style_picker.SetCurrentBoxWidget(self.obj.box_widget)
        # print(self.obj.GetBorderRepresentation().GetInteractionState())

        self.displayer.Render()
