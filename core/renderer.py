# -*- coding: utf-8 -*-
import vtk
from annotation_tools.core.actor import MyActor
from annotation_tools.callbacks.camera_callback import CameraCallback


class Renderer(vtk.vtkRenderer):
    def __init__(self, actors=[], camera=None):
        super().__init__()
        # actor
        for myactor in actors:
            self.AddMyActor(myactor)

        # camera
        self.SetCamera(camera)

    def AddMyActor(self, myactor):
        assert isinstance(myactor,
                          MyActor), print("Only MyActor type is accepted")
        self.AddActor(myactor.actor)

    def SetCamera(self, camera):
        if camera:
            self.camera = camera
        else:
            self.camera = vtk.vtkCamera()

        self.camera.SetPosition(0, 0, 100)
        self.camera.SetFocalPoint(0, 0, 0)
        self.SetActiveCamera(self.camera)

    def SetFocalPoint(self, focal_point):
        self.camera_callback.focal_point = focal_point

    def AddPossibleFocalPoint(self, possible_fp):
        self.camera_callback.AddPossibleFocalPoint(possible_fp)

    def ResetPossibleFocalPoint(self):
        self.camera_callback.ResetPossibleFocalPoint(None, None)

    def RegisterCameraCallback(self, displayer):
        self.camera_callback = CameraCallback(self.camera,
                                              displayer.interactor)
