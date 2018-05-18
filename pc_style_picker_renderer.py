# -*- coding: utf-8 -*-

class PolyDataStylePickerRenderer(StylePickerRenderer):
    def __init__(self, renderer, style=None, picker=None):
        # self.selection = selection
        super().__init__(renderer, style, picker)
        self.cur_box_widget = None

    def SetCurrentBoxWidget(self, box_widget):
        self.cur_box_widget = box_widget

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


