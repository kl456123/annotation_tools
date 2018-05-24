# -*- coding: utf-8 -*-
import vtk
import math

from annotation_tools.core.style_picker_renderer import StylePickerRenderer
from annotation_tools.callbacks.area_picker_callback import AreaPickerCallback
from annotation_tools.callbacks.point_cloud_style_callback import PointCloudStyleCallback
from annotation_tools.utils.geometry_util import GetBoundsCenter
from annotation_tools.core.box_widget import BoxWidget


class PolyDataStylePickerRenderer(StylePickerRenderer):
    def __init__(self, renderer, style=None, picker=None):
        # self.selection = selection
        super().__init__(renderer, style, picker)
        self.cur_box_widget = None
        self.points_actor = None
        self.box_widgets = []

        # this member is shared with image_style_picker_renderer
        self.classes = []

    def ResetClasses(self):
        for c in self.classes:
            del c

    def CloseBoxWidget(self):
        for box in self.box_widgets:
            box.Off()
        self.box_widgets = []

    def Reset(self):
        self.CloseBoxWidget()
        self.ResetClasses()
        self.renderer.ResetPossibleFocalPoint()
        self.points_actor.UpdatePoints()

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

    def AddBoxWidgetFromSelection(self):
        box_widget = self.selection.GetCurrentBoxWidget()

        if not self.selection.IsObjectSelected():
            print("please select first")
            return

        self.box_widgets.append(box_widget)

        # add possible focal point to renderer

        self.renderer.AddPossibleFocalPoint(
            GetBoundsCenter(box_widget.GetBounds()))

    def AddBoxWidgetFromLabel(self, labels, displayer):
        factor = 1
        for label in labels:
            center = label["t"]
            center[1] -= label["h"] / 2.0

            dims = label["h"], label["w"], label["l"]
            dims = [factor * i for i in dims]

            angle = label["yaw"] / math.pi * 180
            box = BoxWidget(self.renderer, displayer)
            box.SetCenterAndDim(center, dims, angle)

            # add possible focal point to renderer
            self.renderer.AddPossibleFocalPoint(
                GetBoundsCenter(box.GetBounds()))
            self.box_widgets.append(box)
            self.classes.append(label["type"])
            displayer.SetColorForBoxWidget(box, label['type'])
            box.On()

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
