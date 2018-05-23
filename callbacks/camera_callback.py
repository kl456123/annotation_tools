# -*- coding: utf-8 -*-

from annotation_tools.callback import Callback
import vtk


class CameraCallback(Callback):
    def __init__(self, camera, interactor):
        super().__init__(camera, interactor=interactor)
        self.focal_point = [0, 0, 0]
        self.possible_fps = [(0, 0, 0)]
        self.idx_fps = 0
        self.slice_height = 30
        self.lower_step = 1
        self.clipping_range = [0.1, 3000]

        self.SetVerticalView(self.obj, None)

    def AutoAdjustCameraPosition(self, obj, event):
        self.position = self.obj.GetPosition()

    def CheckIsCameraHeightChanged(self, position):
        if self.obj.in_velo:
            height_idx = 2
        else:
            height_idx = 1
        return False if self.position[height_idx] == position[
            height_idx] else True

    def AutoAjustClippingRange(self, obj, event):
        self.SetClippingRange()

    def LowerSlice(self, obj, event):
        self.slice_height -= self.lower_step
        self.SetClippingRange()
        self.SetCamera()

    def HigherSlice(self, obj, event):
        self.slice_height += self.lower_step
        self.SetClippingRange()
        self.SetCamera()

    def SetClippingRange(self):
        if self.obj.in_velo:
            near = self.position[2] - self.slice_height
            self.clipping_range[0] = near if near > 0 else 0
            # self.clipping_range[0] = near
        else:
            near = self.slice_height - self.position[1]
            self.clipping_range[0] = near if near > 0 else 0

        self.obj.SetClippingRange(self.clipping_range)

    def AddPossibleFocalPoint(self, possible_focalpoint):
        self.possible_fps.append(possible_focalpoint)

    def ResetPossibleFocalPoint(self, obj, event):
        self.possible_fps = [(0, 0, 0)]

    def SwitchFocalPoint(self, obj, event):
        self.idx_fps = (self.idx_fps + 1) % len(self.possible_fps)
        self.focal_point = self.possible_fps[self.idx_fps]
        self.SetVerticalView(None, None)
        self.SetCamera()

    def RightRotation(self, obj, event):
        self.obj.Azimuth(1)

    def LeftRotation(self, obj, event):
        self.obj.Azimuth(-1)

    def UpRotation(self, obj, event):
        self.obj.Elevation(1)

    def ClockwiseRollRotation(self, obj, event):
        self.obj.Roll(1)

    def CounterclockwiseRollRotation(self, obj, event):
        self.obj.Roll(-1)

    def DownRotation(self, obj, event):
        self.obj.Elevation(-1)

    def SetHorizontalView(self, obj, event):
        # if self.obj.in_velo:
        #     self.position = [-100, self.focal_point[0], self.focal_point[2]]
        #     self.viewup = [0, 0, 1]
        # else:
        self.position = [self.focal_point[0], self.focal_point[1], -100]
        # self.focal_point = [0,0,0]
        self.viewup = [0, -1, 0]
        self.SetCamera()

    def PrintCamera(self, interactor, event):
        print(self.obj)

    def SetVerticalView(self, obj, event):
        # if self.obj.in_velo:
        #     self.position = [self.focal_point[0], self.focal_point[1], 100]
        #     self.viewup = [0, 1, 0]
        # else:
        self.position = [self.focal_point[0], -100, self.focal_point[2]]
        self.viewup = [-1, 0, 0]

        self.SetCamera()

    def ResetCameraView(self, obj, event):
        self.SetVerticalView(obj, event)

    def SetCamera(self):
        self.obj.SetPosition(self.position)
        self.obj.SetFocalPoint(self.focal_point)
        self.obj.SetViewUp(self.viewup)
        self.obj.ComputeViewPlaneNormal()
        self.obj.SetClippingRange(self.clipping_range)

    def Start(self):
        self.AddKeyObserver("v", self.SetVerticalView)
        self.AddKeyObserver("h", self.SetHorizontalView)
        # self.AddKeyObserver("p", self.PrintCamera)
        self.AddKeyObserver("Right", self.RightRotation)
        self.AddKeyObserver("Left", self.LeftRotation)
        self.AddKeyObserver("Down", self.DownRotation)
        self.AddKeyObserver("Up", self.UpRotation)
        self.AddKeyObserver("Tab", self.SwitchFocalPoint)
        # self.AddKeyObserver("n",self.ClockwiseRollRotation)
        # self.AddKeyObserver("m",self.CounterclockwiseRollRotation)
        # self.AddKeyObserver("1", self.LowerSlice)
        # self.AddKeyObserver("2", self.HigherSlice)
        self.AddEventObserver(vtk.vtkCommand.ModifiedEvent,
                              self.AutoAdjustCameraPosition)
        # self.AddEventObserver(vtk.vtkCommand.ModifiedEvent,
        # self.AutoAjustClippingRange)
        # self.AddEventObserver(vtk.vtkCommand.ModifiedEvent,
        # self.AutoAjustClippingRange)
        # self.AddKeyObserver("n",self.ResetPossibleFocalPoint)
