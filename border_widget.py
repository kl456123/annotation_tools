# -*- coding: utf-8 -*-
import vtk
import numpy as np


class BorderWidget(vtk.vtkBorderWidget):
    def __init__(self, start, end, img_start, renderer, displayer):
        super().__init__()
        self.coords = []
        self.SetRenderer(renderer)
        self.interactor = displayer.interactor
        self.img_start = img_start
        self.abs_start = None
        self.abs_end = None
        self.box_widget = None
        self.SetInteractor(self.interactor)
        self.Generate(start, end)
        print("borderwidget callback registered!")
        self.RegisterCallBack(displayer)

    def BindBoxWidget(self, box_widget):
        self.box_widget = box_widget

    def GetInfo(self, img_size):
        rep = self.GetBorderRepresentation()

        pos = np.array(rep.GetPosition())
        pos2 = np.array(rep.GetPosition2())

        pos2 += pos

        # normalized coordinates
        box = np.concatenate([pos, pos2])

        size = list(self.interactor.GetRenderWindow().GetSize())
        # print("size: ",size)

        # view_port size
        size[1] -= self.img_start[1] * size[1]

        # original coordinates

        # box left bottom and right top
        box[::2] *= size[0]
        box[1::2] *= size[1]

        # box left top and right bottom
        a, b = box[1], box[3]

        box[1] = img_size[1] - b
        box[3] = img_size[1] - a

        res1 = list(map(lambda x: round(x, 2), list(box)))

        return res1

    def SetRenderer(self, renderer):
        self.SetDefaultRenderer(renderer)

    def SetPosition(self):
        size = list(self.interactor.GetRenderWindow().GetSize())
        new_original = []
        new_original.append(self.img_start[0] * size[0])
        new_original.append(self.img_start[1] * size[1])

        size[1] -= new_original[1]
        tmp = [self.abs_start[0] / size[0], self.abs_start[1] / size[1]]

        representation = self.GetBorderRepresentation()

        representation.SetPosition(tmp[0], tmp[1])
        representation.SetPosition2(
            self.abs_end[0] / size[0] - tmp[0], self.abs_end[1] / size[1] - tmp[1])

    def Generate(self, start, end):
        new_original = []
        size = list(self.interactor.GetRenderWindow().GetSize())
        new_original.append(self.img_start[0] * size[0])
        new_original.append(self.img_start[1] * size[1])

        new_start = [start[0], end[1]-new_original[1]]
        new_end = [end[0], start[1]-new_original[1]]

        self.abs_start = new_start
        self.abs_end = new_end

        self.coords += new_start
        self.coords += new_end

        size[1] -= new_original[1]
        tmp = [new_start[0] / size[0], new_start[1] / size[1]]

        self.CreateDefaultRepresentation()
        representation = self.GetBorderRepresentation()

        representation.SetPosition(tmp[0], tmp[1])
        representation.SetPosition2(
            new_end[0]/size[0]-tmp[0], new_end[1]/size[1]-tmp[1])
        representation.NeedToRenderOn()
        representation.MovingOff()
        # self.SetRepresentation(representation)
        self.SetInteractor(self.interactor)
        self.SelectableOff()
        # self.SetResizable(1)

        # self.ResizableOn()
        self.KeyPressActivationOff()
        self.ManagesCursorOff()

        print("border widget activated! ")
        self.On()
        # print(self.GetBorderRepresentation().GetInteractionState())
        # print(representation)

    def ChangeColor(self, color_name=[1, 1, 0]):
        self.GetBorderRepresentation().GetBorderProperty().SetColor(color_name)

    def UnchangeColor(self):
        self.GetBorderRepresentation().GetBorderProperty().SetColor([1, 1, 1])

    def RegisterCallBack(self, displayer):
        from callback import BorderWidgetCallback
        self.callback = BorderWidgetCallback(self, displayer)
