# -*- coding: utf-8 -*-
import vtk

from annotation_tools.callbacks.render_window_callback import RenderWindowCallback


class RenderWindow(vtk.vtkRenderWindow):
    def __init__(self):
        super().__init__()
        self._window_size = None
        # self._title = ""
        # self.RegisterRenderWindowCallback()

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, window_size):
        self._window_size = window_size

    # @property
    # def title(self):
        # return self._title

    # @title.setter
    # def title(self, title):
        # self._title = title

    def RegisterRenderWindowCallback(self, displayer):
        self.callback = RenderWindowCallback(self, displayer)
