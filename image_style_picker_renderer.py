# -*- coding: utf-8 -*-

from StylePickerRenderer
class ImageStylePickerRenderer(StylePickerRenderer):
    def __init__(self, renderer, selection, style=None, picker=None, myactor=None):
        super().__init__(renderer, style, picker)
        self.myactor = myactor
        self.selection = selection
        self.border_widgets_idx = 0
        self.border_widgets = []
        self.img_size = None
        self.cur_border_widget = None

        # default is the last one to mark "selected"
        self.selected_border_idx = -1

    def SetImageSize(self, img_size):
        self.img_size = img_size

    def SetSelectedIdx(self, idx):
        # TODO check it is legal first
        self.selected_border_idx = idx

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

    def SetPicker(self, picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = None

    def RegisterStyleCallback(self, displayer, img_start):
        # pass
        self.style_callback = ImageStyleCallback(
            self.style, self, displayer, self.selection, img_start)

    def RegisterPickerCallback(self, displayer):
        pass

    def On(self):
        self.style.On()

    def Off(self):
        self.style.Off()

    def CloseLastBorderWidget(self):
        for border in self.border_widgets:
            border.Off()
        self.border_widgets = []

