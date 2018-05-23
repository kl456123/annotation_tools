# -*- coding: utf-8 -*-

import vtk

from annotation_tools.callback import PickerCallback
from annotation_tools.utils.geometry_util import DeepCopyPlanes

class AreaPickerCallback(PickerCallback):
    def __init__(self, picker, displayer):
        super().__init__(picker, interactor=displayer.interactor)
        self.displayer = displayer
        # self.selection = displayer.selection

    def EndPickEvent(self, obj, event):
        # fix bug (have to use deep copy here)
        frustum = DeepCopyPlanes(self.obj.GetFrustum())

        self.displayer.selection.AddFilter(frustum)

        # color it
        self.displayer.selection.Color()

        # render again
        self.displayer.Render()

    def SelectionContinueOff(self, obj, event):
        self.displayer.selection.SetContinue(False)

    def SelectionContinueOn(self, obj, event):
        self.displayer.selection.SetContinue(True)

    def Start(self):
        # add key observer
        self.AddKeyObserver("c", self.SelectionContinueOn)
        self.AddKeyObserver("s", self.SelectionContinueOff)

        # add event observer
        self.AddEventObserver(vtk.vtkCommand.EndPickEvent, self.EndPickEvent)
