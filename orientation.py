from utils import *

class CameraView(object):
    def __init__(self,camera):
        self.camera = camera
        # default view
        self.SetVerticalView(None,None)

    def PrintCamera(self,interactor,event):
        print(self.camera)

    def SetHorizontalView(self,interactor,event):
        self.position = [-100,0,0]
        self.focal_point = [0,0,0]
        self.viewup = [0,0,1]
        self.SetCamera()

    def SetImageView(self,interactor,event):
        # self.viewup, self.position, self.focal_point = \
        #     GenerateCameraParameter()
        # camera = vtk.vtkCamera()
        #
        # camera.SetModelTransformMatrix(ConvertNumpy2VTK(GetExtrinsicMatrix()))

        # camera.UseExplicitProjectionTransformMatrixOn()
        # camera.SetExplicitProjectionTransformMatrix(ConvertNumpy2VTK(GetIntrinsicMatrix()))
        # camera.GetCompositeProjectionTransformMatrix()
        self.camera = camera



    def SetVerticalView(self,interactor , event):
        self.position = [0,0,100]
        self.focal_point = [0,0,0]
        self.viewup = [0,1,0]
        self.SetCamera()

    def ChangeFocalPoint(self,interactor,event):
        self.focal_point = [0,0,20]
        self.SetCamera()


    def SetCamera(self):
        self.camera.SetPosition(self.position)
        self.camera.SetFocalPoint(self.focal_point)
        self.camera.SetViewUp(self.viewup)

    def AddObserver(self,key_control):
        # add more key function here
        key_control.AddKeyObserver("h",self.SetHorizontalView)
        key_control.AddKeyObserver("v",self.SetVerticalView)
        key_control.AddKeyObserver("j",self.SetImageView)
        key_control.AddKeyObserver("x",self.ChangeFocalPoint)
        key_control.AddKeyObserver("p",self.PrintCamera)