# -*- coding: utf-8 -*-
import vtk

from annotation_tools.core.style_picker_renderer import StylePickerRenderer
from annotation_tools.callbacks.area_picker_callback import AreaPickerCallback
from annotation_tools.callbacks.point_cloud_style_callback import PointCloudStyleCallback


class PolyDataStylePickerRenderer(StylePickerRenderer):
    def __init__(self, renderer, style=None, picker=None):
        # self.selection = selection
        super().__init__(renderer, style, picker)
        self.cur_box_widget = None
        self.points_actor = None

    def SetCurrentBoxWidget(self, box_widget):
        # self.cur_box_widget = box_widget
        if box_widget is None:
            self.cur_box_widget = None
        else:
            if self.cur_box_widget:
                self.cur_box_widget.UnchangeColor()

            box_widget.ChangeColor()
            self.cur_box_widget = box_widget

    def SetPointsActor(self, points_actor):
        self.points_actor = points_actor

    def GetCurrentBoxWidget(self):
        if self.cur_box_widget:
            return self.cur_box_widget
        else:
            print("ERROR: box widget is not selected")
            return None

    def SetPicker(self, picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = vtk.vtkAreaPicker()

    def SetSelection(self, selection):
        self.selection = selection

    def SetStyle(self, style=None):
        if style:
            self.style = style
        else:
            self.style = vtk.vtkInteractorStyleRubberBandPick()

    def RegisterPickerCallback(self, displayer):
        self.picker_callback = AreaPickerCallback(self.picker, displayer)

    def RegisterStyleCallback(self, displayer):
        self.style_callback = PointCloudStyleCallback(
            self.style, self, displayer=displayer)
