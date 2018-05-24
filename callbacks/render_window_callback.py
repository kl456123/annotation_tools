# -*- coding: utf-8 -*-

from annotation_tools.callback import Callback


class RenderWindowCallback(Callback):
    def __init__(self, obj, displayer, debug=False):
        super().__init__(obj, debug, displayer.interactor)
        self.displayer = displayer

    def AdjustWindowSize(self, obj, event):
        size = self.obj.GetSize()
        if size == self.obj.window_size:
            return
        self.obj.window_size = size

        if not self.displayer.dataset.velo_only:

            for border in self.displayer.img_style_picker.border_widgets:
                border.SetPosition()

    def Start(self):
        self.AddEventObserver("ModifiedEvent", self.AdjustWindowSize)
