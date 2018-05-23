# -*- coding: utf-8 -*-

from abc import ABC, abstractclassmethod


class StylePickerRenderer(ABC):
    def __init__(self, renderer, style=None, picker=None):
        self.renderer = renderer
        # self.SetRenderer(myactors)
        self.SetPicker(picker)
        self.SetStyle(style)

    @abstractclassmethod
    def SetPicker(self, picker=None):
        pass

    @abstractclassmethod
    def SetStyle(self, style=None):
        pass

    @abstractclassmethod
    def RegisterPickerCallback(self, displayer):
        pass

    @abstractclassmethod
    def RegisterStyleCallback(self, displayer):
        pass
