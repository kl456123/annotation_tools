# -*- coding: utf-8 -*-

from annotation_tools.callback import StyleCallback, Callback
import vtk


class PointCloudStyleCallback(StyleCallback):
    def __init__(self, obj, style_picker_renderer, debug=False,
                 displayer=None):
        super().__init__(obj, debug, displayer.interactor)
        self.mode = "view"
        self.style_picker_renderer = style_picker_renderer
        self.displayer = displayer
        self.height = 30
        self.step = 1
        self.velo_only = self.displayer.velo_only

    def ChangeWindowName(self, obj, event):
        if self.mode == "view":
            self.mode = "rubber"
        else:
            self.mode = "view"
        self.displayer.SetWindowName()
        #
        # window = self.interactor.GetRenderWindow()
        # title = window.GetWindowName()
        # title = title.split(":")[0]
        #
        # title += ":"
        # title += self.mode
        # window.SetWindowName(title)

    def LowerSlice(self, obj, event):
        self.height -= self.step
        self.SlicePointCloud()

    def SlicePointCloud(self):
        points_actor = self.style_picker_renderer.points_actor
        height_axis = 1
        points_actor.RemoveHigherPoints(self.height, height_axis)

    def HigherSlice(self, obj, event):
        self.height += self.step
        self.SlicePointCloud()

    def Reset(self, obj, event):
        cur = self.style_picker_renderer.GetCurrentBoxWidget()
        # displayer = self.displayer

        if cur:
            for idx, box in enumerate(self.displayer.box_widgets):
                if cur is box:
                    box.Off()
                    del self.displayer.box_widgets[idx]

    def Start(self):
        self.AddKeyObserver("r", self.ChangeWindowName)
        self.AddKeyObserver("2", self.HigherSlice)
        self.AddKeyObserver("1", self.LowerSlice)
        self.AddKeyObserver("4", self.Reset)



