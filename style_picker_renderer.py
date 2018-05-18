# -*- coding: utf-8 -*-

class StylePickerRenderer(object):
    def __init__(self, renderer, style=None, picker=None):
        self.renderer = renderer
        # self.SetRenderer(myactors)
        self.SetPicker(picker)
        self.SetStyle(style)

    def SetPicker(self, picker=None):
        pass

    def SetStyle(self, style=None):
        pass

    def RegisterPickerCallback(self, displayer):
        pass

    def RegisterStyleCallback(self, displayer):
        pass


