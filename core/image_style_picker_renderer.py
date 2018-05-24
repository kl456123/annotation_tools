# -*- coding: utf-8 -*-
import vtk

from annotation_tools.core.style_picker_renderer import StylePickerRenderer
from annotation_tools.callbacks.image_style_callback import ImageStyleCallback
from annotation_tools.core.border_widget import BorderWidget


class ImageStylePickerRenderer(StylePickerRenderer):
    def __init__(self,
                 renderer,
                 selection,
                 style=None,
                 picker=None,
                 myactor=None):
        super().__init__(renderer, style, picker)
        self.myactor = myactor
        self.selection = selection
        self.border_widgets_idx = 0
        self.border_widgets = []
        self.img_size = None
        self.cur_border_widget = None

        # default is the last one to mark "selected"
        self.selected_border_idx = -1
        self.classes = []

    def SetImageSize(self, img_size):
        self.img_size = img_size

    # def SetSelectedIdx(self, idx):
    # TODO check it is legal first
    # self.selected_border_idx = idx

    def SetCurrentBorderWidget(self, border_widget):
        if border_widget is None:
            self.cur_border_widget = None
        else:

            if self.cur_border_widget:
                self.cur_border_widget.UnchangeColor()

            border_widget.ChangeColor()
            self.cur_border_widget = border_widget

    def GetCurrentBorderWidget(self):
        if self.cur_border_widget:
            return self.cur_border_widget
        # if len(self.border_widgets)>0:
        #     return self.border_widgets[-1]
        else:
            print("ERROR: border widget is not selected")
            return

    def IncreaseIdx(self):
        self.border_widgets_idx += len(self.border_widgets)

    def SetStyle(self, style=None):
        if style:
            self.style = style
        else:
            self.style = vtk.vtkInteractorStyleRubberBand2D()
        # self.style.Off()

    def SetPicker(self, picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = None

    def RegisterStyleCallback(self, displayer, img_start):
        # pass
        self.style_callback = ImageStyleCallback(self.style, self, displayer,
                                                 self.selection, img_start)

    def RegisterPickerCallback(self, displayer):
        pass

    def On(self):
        self.style.On()

    def Off(self):
        self.style.Off()

    def CloseBorderWidget(self):
        for border in self.border_widgets:
            border.Off()

        self.border_widgets = []

    def ResetClasses(self):
        for c in self.classes:
            del c

    def Reset(self):
        self.ResetClasses()
        self.CloseBorderWidget()

    def AddBorderWidgetFromLabel(self, labels, displayer):
        size = displayer.interactor.GetRenderWindow().GetSize()
        for label in labels:
            box2d = label["box2d"]
            a, b = box2d[1], box2d[3]
            img_size = self.img_size

            box2d[1] = img_size[1] - a
            box2d[3] = img_size[1] - b

            img_view_port = self.renderer.GetViewport()
            img_start = img_view_port[:2]

            box2d[1] += img_start[1] * size[1]
            box2d[3] += img_start[1] * size[1]

            border_widget = BorderWidget(box2d[:2], box2d[2:],
                                         img_view_port[:2], self.renderer,
                                         displayer)
            # bind with it
            # border_widget.BindBoxWidget(box)

            self.border_widgets.append(border_widget)
