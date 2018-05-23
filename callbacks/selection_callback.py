# -*- coding: utf-8 -*-
from annotation_tools.callback import Callback
from annotation_tools.utils.geometry_util import GetBoundsCenter
import numpy as np
import vtk


class SelectionCallback(Callback):
    def __init__(self, selection, debug=False):
        super().__init__(selection, debug, selection.displayer.interactor)

        # inner variable
        self.transform = vtk.vtkTransform()
        self.transform.PostMultiply()
        self.angle_step = 1

    def SetBoxCenterFocalPoint(self, obj, event):
        # switch focal point to center of box
        box_widget = self.obj.GetCurrentBoxWidget()
        center = GetBoundsCenter(box_widget.GetBounds())
        renderer = self.obj.displayer.GetPointCloudRenderer()
        renderer.SetFocalPoint(center)

    def ClockwiseRotate(self, obj, event):
        self.angle_step = 1
        self.RotateBoxWidget()

    def CounterclockwiseRotate(self, obj, event):
        self.angle_step = -1
        self.RotateBoxWidget()

    # def TestAdd(self,obj,event):
    #     print("adsga")

    def RotateBoxWidget(self):
        box_widget = self.obj.GetCurrentBoxWidget()

        init_center = box_widget.init_center
        if init_center is None:
            print("please select region first! ")
            return

        self.obj.angle += self.angle_step
        self.transform.Identity()
        #
        center = GetBoundsCenter(box_widget.GetBounds())

        # get scale
        t = vtk.vtkTransform()
        box_widget.GetTransform(t)
        scale = t.GetScale()

        # create transform
        self.transform.Identity()
        self.transform.Translate(
            [-init_center[0], -init_center[1], -init_center[2]])

        # scale
        self.transform.Scale(scale)

        # rotation
        # if self.obj.in_velo:
        #     self.transform.RotateZ(self.obj.angle)
        # else:
        self.transform.RotateY(self.obj.angle)

        box_widget.SetAngle(self.obj.angle)

        # translation back
        self.transform.Translate(center)

        # apply
        box_widget.SetTransform(self.transform)

    def Reset(self, obj, event):
        self.obj.Reset()

    def Start(self):
        self.AddKeyObserver("z", self.ClockwiseRotate)
        self.AddKeyObserver("x", self.CounterclockwiseRotate)
        self.AddKeyObserver("b", self.SetBoxCenterFocalPoint)
        self.AddKeyObserver("4", self.Reset)
        # self.AddKeyObserver("a",self.TestAdd)
