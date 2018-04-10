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

    @abstractclassmethod
    def SetPicker(self,picker=None):
        pass

    @abstractclassmethod
    def SetStyle(self,style=None):
        pass

    @abstractclassmethod
    def RegisterPickerCallback(self,displayer):
        pass

    @abstractclassmethod
    def RegisterStyleCallback(self,displayer):
        pass

class ImageStylePickerRenderer(StylePickerRenderer):
    def __init__(self, renderer,selection,style=None, picker=None,myactor=None):
        super().__init__(renderer,style,picker)
        self.myactor = myactor
        self.selection = selection
        self.border_widgets = []

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
        pass


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


    def SetInteractor(self):
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

    def Render(self):
        self.window.Render()

    def Start(self):
        self.interactor.Initialize()
        self.interactor.Start()

    @abstractclassmethod
    def RegisterDisplayerCallback(self):
        pass

class StylePickerDisplayer(Displayer):
    def __init__(self):
        super().__init__()
        self.StylePickerRenderers = []
        self.current_renderer = None
        self.current_idx = None
        self.box_widgets = []

        # default the first one is for point cloud displayer
        self.poly_style_idx= 0
        self.img_style_idx=1
        self.need_save_idx = 0

    def SetFileName(self,filename):
        self.filename = filename

    def SetSelection(self,selection):
        self.selection = selection

    def AddStylePickerRenderer(self,stylePickerRenderer):
        self.StylePickerRenderers.append(stylePickerRenderer)
        self.window.AddRenderer(stylePickerRenderer.renderer)

    def GetPointCloudRenderer(self):
        return self.StylePickerRenderers[self.poly_style_idx].renderer

    def AddBoxWidget(self):
        box_widget = self.selection.GetCurrentBoxWidget()
        if not box_widget.myactor:
            print("please select first")
            return
        self.box_widgets.append(box_widget)

        # add possible focal point to renderer
        point_renderer = self.StylePickerRenderers[self.poly_style_idx]
        point_renderer.renderer.AddPossibleFocalPoint(GetBoundsCenter(box_widget.GetBounds()))

    def AddConstumBoxWidget(self):
        pass

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

    def RegisterDisplayerCallback(self):
        self.callback = DisplayerCallback(self)
