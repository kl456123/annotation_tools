import vtk
from actor import MyActor
from callback import *
from abc import  ABCMeta,abstractclassmethod
from box_widget import *

class Renderer(vtk.vtkRenderer):
    def __init__(self,actors=[],camera=None):
        super().__init__()
        # actor
        for myactor in actors:
            self.AddMyActor(myactor)

        # camera
        self.SetCamera(camera)

    def AddMyActor(self,myactor):
        assert isinstance(myactor, MyActor), print("Only MyActor type is accepted")
        self.AddActor(myactor.actor)

    def SetCamera(self,camera):
        if camera:
            self.camera = camera
        else:
            self.camera = vtk.vtkCamera()

        self.camera.SetPosition(0, 0, 100)
        self.camera.SetFocalPoint(0, 0, 0)
        self.SetActiveCamera(self.camera)

    def SetFocalPoint(self,focal_point):
        self.camera_callback.focal_point = focal_point

    def AddPossibleFocalPoint(self,possible_fp):
        self.camera_callback.AddPossibleFocalPoint(possible_fp)

    def RegisterCameraCallback(self,displayer):
        self.camera_callback = CameraCallback(self.camera,displayer.interactor)

class StylePickerRenderer(object):
    __metaclass__ = ABCMeta
    def __init__(self,renderer,style=None,picker=None):
        self.renderer = renderer
        # self.SetRenderer(myactors)
        self.SetPicker(picker)
        self.SetStyle(style)

    def SetPicker(self,picker=None):
        pass

    def SetStyle(self,style=None):
        pass

    def RegisterPickerCallback(self,displayer):
        pass

    def RegisterStyleCallback(self,displayer):
        pass

class ImageStylePickerRenderer(StylePickerRenderer):
    def __init__(self, renderer,selection,style=None, picker=None,myactor=None):
        super().__init__(renderer,style,picker)
        self.myactor = myactor
        self.selection = selection
        self.border_widgets_idx = 0
        self.border_widgets = []
        self.img_size = None

    def SetImageSize(self,img_size):
        self.img_size = img_size

    def IncreaseIdx(self):
        self.border_widgets_idx+=len(self.border_widgets)

    def SetStyle(self,style=None):
        if style:
            self.style = style
        else:
            self.style = vtk.vtkInteractorStyleRubberBand2D()

    def SetPicker(self,picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = None

    def RegisterStyleCallback(self,displayer,img_start):
        # pass
        self.style_callback = ImageStyleCallback(self.style,self,displayer,self.selection,self.myactor,img_start)

    def RegisterPickerCallback(self,displayer):
        pass
        # self.picker_callback = ImagePickerCallback(self.picker)

    def CloseLastBorderWidget(self):
        for border in self.border_widgets:
            border.Off()
        self.border_widgets = []

class PolyDataStylePickerRenderer(StylePickerRenderer):
    def __init__(self,renderer,selection=None,style=None,picker=None):
        self.selection = selection
        super().__init__(renderer,style,picker)

    def SetPicker(self,picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = vtk.vtkAreaPicker()

    def SetStyle(self,style=None):
        if style:
            self.style = style
        else:
            self.style = vtk.vtkInteractorStyleRubberBandPick()


    def RegisterPickerCallback(self,displayer):
        self.picker_callback = AreaPickerCallback(self.picker,displayer,self.selection)

    def RegisterStyleCallback(self,displayer):
        self.style_callback = PointCloudStyleCallback(self.style,interactor=displayer.interactor)

    # def CloseLastBoxWidget(self):
    #     self


class Displayer(object):
    __metaclass__ = ABCMeta

    def __init__(self):

        self.SetWindow()

        self.SetInteractor()

        self.RegisterDisplayerCallback()

    def AddRenderer(self,renderer):
        if renderer:
            self.window.AddRenderer(renderer)

    def SetWindow(self):
        self.window = vtk.vtkRenderWindow()


    def SetDataSet(self,dataset):
        self.dataset = dataset


    def SetInteractor(self):
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

    def Render(self):
        self.window.Render()


    def Start(self):
        self.interactor.Initialize()
        self.interactor.Start()

    def RegisterDisplayerCallback(self):
        pass

class StylePickerDisplayer(Displayer):
    def __init__(self,cfg):
        super().__init__()
        self.current_renderer = None
        self.current_idx = None
        self.box_widgets = []
        self.classes = []
        self.StylePickerRenderers = []
        # self.orientation = []
        # print(cfg)
        self.auto_save = cfg["auto_save"]
        self.mode = cfg["mode"]

        self.img_style_flag = False

    def AddLabelWidget(self,labels):
        factor = 1
        for label in labels:
            center = label["t"]
            center[1]-=label["h"]/2.0
            # center = [center[2],center[0],center[1]]
            # new_center = [center[1],center[0],center[2]]
            # center =   [1.74, 0.56 ,8.33]
            # center = new_center
            dims = label["h"],label["w"], label["l"]
            dims = [factor*i for i in dims]

            angle = label["yaw"]/math.pi*180
            # angle=0
            box = BoxWidget(self.pc_style_picker.renderer,self)
            # print(dims)
            box.SetCenterAndDim(center,dims,angle)
            # box.SetPlaceFactor(10)
            # bounds = GetBounds(center,dims)
            # print(bounds)
            # bounds = [-1, 1, -1, 1, -1, 1]
            # box.PlaceWidget(bounds)
            box.On()
            self.box_widgets.append(box)

    def SetImgStylePicker(self,img_style_picker):
        self.img_style_picker = img_style_picker
        self.AddStylePickerRenderer(img_style_picker)

    def SetPointCloudStylePicker(self,pc_style_picker):
        self.pc_style_picker = pc_style_picker
        self.AddStylePickerRenderer(pc_style_picker)

    def InputClass(self):
        class_idx = input("please input index of classes:")
        # print(type(class_idx))
        self.classes.append(class_idx)

    def InputOrientation(self):
        orientation_idx = input("please input index of plane:")
        # print(type(orientation_idx))
        self.box_widgets[-1].orientation = int(orientation_idx)
        # self.orientation.append(orientation_idx)

    def CloseLastBoxWidget(self):
        # close border widgets
        self.img_style_picker.CloseLastBorderWidget()

        for box in self.box_widgets:
            box.Off()
        self.box_widgets = []

    def SetWindowName(self):
        title = "the {}th:{}".format(str(self.dataset.data_idx+1),
                                     self.pc_style_picker.style_callback.mode)
        self.window.SetWindowName(title)

    def SetLabelName(self,label_name):
        self.label_name = label_name

    def Start(self):
        self.dataset.LoadNext()
        self.Render()
        self.SetWindowName()
        self.img_style_picker.SetImageSize(self.dataset.GetImageSize())
        if self.mode=="display":
            self.dataset.LoadLabel(self.label_name)
            self.dataset.ParseLabel()
            self.AddLabelWidget(self.dataset.label)
        super().Start()

    def GetWidgetIdx(self):
        return self.img_style_picker.border_widgets_idx


    def SetPointActor(self,myactor):
        self.point_actor = myactor

    def SetImageActor(self,myactor):
        self.img_actor = myactor

    def SetFileName(self,filename):
        self.filename = filename

    def SetSelection(self,selection):
        self.selection = selection

    def AddStylePickerRenderer(self,stylePickerRenderer):
        self.StylePickerRenderers.append(stylePickerRenderer)
        self.window.AddRenderer(stylePickerRenderer.renderer)

    def GetPointCloudRenderer(self):
        return self.pc_style_picker.renderer

    def AddBoxWidget(self):
        box_widget = self.selection.GetCurrentBoxWidget()
        if not box_widget.myactor:
            print("please select first")
            return
        self.box_widgets.append(box_widget)

        # add possible focal point to renderer
        point_renderer = self.pc_style_picker
        point_renderer.renderer.AddPossibleFocalPoint(GetBoundsCenter(box_widget.GetBounds()))

    def SwitchStylePicker(self,idx):
        if self.current_idx==idx:
            return
        stylePickerRenderer = self.StylePickerRenderers[idx]
        self.current_renderer = stylePickerRenderer.renderer

        picker = stylePickerRenderer.picker
        style = stylePickerRenderer.style
        if picker:
            self.interactor.SetPicker(picker)
        if style:
            self.interactor.SetInteractorStyle(style)

    def _CheckInSide(self,pos,region):
        x,y = pos
        if region[0]<=x and region[2]>x and region[1]<=y and region[3]>y:
            return  True
        return False

    def SwitchCondition(self,pos):
        for idx,stylePickerRenderer in enumerate(self.StylePickerRenderers):
            region = list(stylePickerRenderer.renderer.GetViewport())
            size = self.interactor.GetRenderWindow().GetSize()
            region[0]*=size[0]
            region[1]*=size[1]
            region[2]*=size[0]
            region[3]*=size[1]
            if self._CheckInSide(pos,region):
                return idx

    # def CheckPosInImage(self,pos):



    def RegisterDisplayerCallback(self):
        self.callback = DisplayerCallback(self)
