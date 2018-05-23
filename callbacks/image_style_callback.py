# -*- coding: utf-8 -*-

from annotation_tools.callback import StyleCallback
from annotation_tools.utils.geometry_util import get_frustum_points_of_box2d, GenerateImplicitFunction
from annotation_tools.core.border_widget import BorderWidget


class ImageStyleCallback(StyleCallback):
    def __init__(self,
                 obj,
                 style_picker_renderer,
                 displayer=None,
                 selection=None,
                 img_start=[0, 0],
                 debug=False):
        super().__init__(obj, debug, displayer.interactor)
        self.displayer = displayer
        # self.myactor = myactor
        self.img_start = img_start
        self.selection = selection
        self.style_picker_renderer = style_picker_renderer

    def ToggleStyle(self, obj, event):
        if self.obj.GetEnabled():
            self.obj.Off()
        else:
            self.obj.On()

    def _ConvertPosToBox(self, start, end):
        size = self.displayer.interactor.GetRenderWindow().GetSize()
        new_original = []
        new_original.append(self.img_start[0] * size[0])
        new_original.append(self.img_start[1] * size[1])
        img_size = self.style_picker_renderer.img_size

        # translation of origin
        start[0] -= new_original[0]
        start[1] -= new_original[1]

        end[0] -= new_original[0]
        end[1] -= new_original[1]

        # flip
        start[1] = img_size[1] - start[1]
        end[1] = img_size[1] - end[1]

        return start + end

    def GenerateImplicitFunction(self, box):
        P = self.displayer.dataset.pc_reader.calib["P2"]
        planes = get_frustum_points_of_box2d(P, box)
        return GenerateImplicitFunction(planes)

    def SelectionChangedEvent(self, obj, event):
        # pass
        start = list(self.obj.GetStartPosition())
        end = list(self.obj.GetEndPosition())
        print("press start end: ", start, end)
        if start == end:
            print("Don't just click,It just draw a point!")
            return
        ######################################
        #####generate box in 2D image#########
        border_widget = BorderWidget(start, end, self.img_start,
                                     self.style_picker_renderer.renderer,
                                     self.displayer)
        self.style_picker_renderer.SetCurrentBorderWidget(border_widget)
        # border_widget.SetRenderer(self.style_picker_renderer.renderer)
        border_widget.BindBoxWidget(self.selection.GetCurrentBoxWidget())
        self.style_picker_renderer.border_widgets.append(border_widget)

        box = self._ConvertPosToBox(start, end)
        # print(box)
        planes = self.GenerateImplicitFunction(box)

        self.selection.AddFilter(planes)

        # color it
        self.selection.Color()

        # set continue for selection for convenience
        self.selection.SetContinue(True)

        # render again
        self.displayer.Render()

    def Reset(self, obj, event):
        # idx = self.style_picker_renderer.selected_border_idx
        current_border = self.style_picker_renderer.GetCurrentBorderWidget()
        print("num of borders in image",
              len(self.style_picker_renderer.border_widgets))
        for idx, border in enumerate(
                self.style_picker_renderer.border_widgets):
            if current_border is border:
                border.Off()
                del self.style_picker_renderer.border_widgets[idx]
                self.style_picker_renderer.SetCurrentBorderWidget(None)
                break

    # def ToggleStyle(self,obj,event):
    #     print("image style status:",self.obj.GetEnabled())
    #     if self.obj.GetEnabled():
    #         self.obj.Off()
    #     else:
    #         self.obj.On()

    def Start(self):
        # pass
        self.AddEventObserver("SelectionChangedEvent",
                              self.SelectionChangedEvent)
        # self.AddKeyObserver("o",self.ToggleWidgetProcess)
        self.AddKeyObserver("4", self.Reset)
        self.AddKeyObserver("5", self.ToggleStyle)
        # self.AddKeyObserver("8",self.ToggleStyle)
