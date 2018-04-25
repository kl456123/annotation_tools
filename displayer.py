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

    def ResetPossibleFocalPoint(self):
        self.camera_callback.ResetPossibleFocalPoint(None,None)

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
        # self.style.Off()

    def SetPicker(self,picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = None

    def RegisterStyleCallback(self,displayer,img_start):
        # pass
        self.style_callback = ImageStyleCallback(self.style,self,displayer,self.selection,img_start)

    def RegisterPickerCallback(self,displayer):
        pass
        # self.picker_callback = ImagePickerCallback(self.picker)

    def CloseLastBorderWidget(self):
        for border in self.border_widgets:
            border.Off()
            # border.SetEnabled(0)
            # self.renderer.RemoveActor(border)
        self.border_widgets = []
        # self.renderer.RemoveAllViewProps()


class PolyDataStylePickerRenderer(StylePickerRenderer):
    def __init__(self,renderer,style=None,picker=None):
        # self.selection = selection
        super().__init__(renderer,style,picker)

    def SetPicker(self,picker=None):
        if picker:
            self.picker = picker
        else:
            self.picker = vtk.vtkAreaPicker()

    def SetSelection(self,selection):
        self.selection = selection

    def SetStyle(self,style=None):
        if style:
            self.style = style
        else:
            self.style = vtk.vtkInteractorStyleRubberBandPick()


    def RegisterPickerCallback(self,displayer):
        self.picker_callback = AreaPickerCallback(self.picker,displayer)

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

        # self.window.SetFullScreen()
        # print("screen size: ",self.window.GetSize())

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

from selection import *
class StylePickerDisplayer(Displayer):
    def __init__(self,dataset,cfg):
        super().__init__()
        self.current_renderer = None
        self.current_idx = None
        self.box_widgets = []
        self.classes = []
        self.StylePickerRenderers = []

        self.auto_save = cfg["auto_save"]
        self.mode = cfg["mode"]

        self.window.SetSize(cfg["window_size"])

        self.img_style_flag = False

        # set in order

        self.SetDataSet(dataset)

        self.SetUpPCStylePickerRenderer(cfg["pc"])

        self.SetUpSelection(cfg["selection"])

        self.SetUpImgStylePickerRenderer(cfg["img"])

    def SetUpSelection(self,selection_cfg):
        # build selection
        selection = Selection(self.dataset.pc_reader.GetFilter(),
                              displayer=self,
                              point_renderer=self.pc_style_picker.renderer,
                              debug=selection_cfg["debug"])
        self.SetSelection(selection)

    def SetUpImgStylePickerRenderer(self,img_cfg):
        # build img style picker renderer
        view_port = img_cfg["view_port"]
        bg = img_cfg["bg"]

        # build renderer and actor
        img_renderer = Renderer()

        img_actor = ImageActor(self.dataset.img_reader.GetOutputPort())
        img_renderer.AddMyActor(img_actor)

        img_style_picker = ImageStylePickerRenderer(img_renderer, self.selection)

        # register callback for img_style_picker
        img_style_picker.RegisterStyleCallback(self, [view_port[0], view_port[1]])
        img_style_picker.renderer.SetViewport(view_port)
        img_style_picker.renderer.SetBackground(bg)

        self.SetImgStylePicker(img_style_picker)



    def SetUpPCStylePickerRenderer(self,pc_cfg):
        # build pc style picker renderer

        # actor
        points_actor = PolyDataActor(self.dataset.pc_reader.GetFilter())

        # renderer
        point_renderer = Renderer([points_actor])

        # register callback for point renderer
        point_renderer.RegisterCameraCallback(self)

        # pc_style_picker
        pc_style_picker = PolyDataStylePickerRenderer(point_renderer)

        # pc_style_picker
        pc_style_picker.RegisterPickerCallback(self)
        pc_style_picker.RegisterStyleCallback(self)

        view_port = pc_cfg["view_port"]

        pc_style_picker.renderer.SetViewport(view_port)


        self.SetPointCloudStylePicker(pc_style_picker)



    def AdjustBoxWidgetsColor(self):
        for idx, box_widget in enumerate(self.box_widgets):
            if idx==0:
                box_widget.AdjustColor(False)
            else:
                box_widget.AdjustColor(True)

    def Reset(self):

        self.CloseLastBoxWidget()
        self.classes = []
        self.pc_style_picker.renderer.ResetPossibleFocalPoint()

        # clean actor in renderer
        print("num: ",self.pc_style_picker.renderer.GetNumberOfPropsRendered())

    def Init(self):
        # init parameters according to loaded data

        # init window title
        self.Render()
        self.SetWindowName()
        self.img_style_picker.SetImageSize(self.dataset.GetImageSize())
        self.AddLabelWidgets(self.dataset.label)
        # self.AddLabelClasses(self.dataset.label)

    def SetLabel(self):
        all_info = []
        box_2D = self.img_style_picker.border_widgets
        for idx, box_3D in  enumerate(self.box_widgets):
            # the num is 16 in all
            info = []
            # 1
            info.append(self.classes[idx])
            # 2
            info.extend(GetTruncatedAndOccluded())
            # 1
            info.append(GetObserverAngle(box_3D))
            # 4
            info.extend(box_2D[idx].GetInfo(self.dataset.GetImageSize()))
            # 7
            info.extend(box_3D.GetInfo())

            # fake score
            # 1
            # info.extend([1.0])

            all_info.append(info)

        self.dataset.SetLabel(all_info)
        print("INFO:Save Label success! ")


        self.dataset.SaveStatus()

    def SaveLabel(self):
        # if self.auto_save:
            # save to list(in memory not in disk)
        self.SetLabel()

        # in disk
        self.dataset.SaveLabel()


    def AddLabelWidgets(self,labels):
        factor = 1
        for label in labels:
            center = label["t"]
            center[1]-=label["h"]/2.0

            dims = label["h"],label["w"], label["l"]
            dims = [factor*i for i in dims]

            angle = label["yaw"]/math.pi*180
            # angle=0
            box = BoxWidget(self.pc_style_picker.renderer,self)
            # print(dims)
            box.SetCenterAndDim(center,dims,angle)

            box.On()
            # add possible focal point to renderer
            point_renderer = self.pc_style_picker
            point_renderer.renderer.AddPossibleFocalPoint(GetBoundsCenter(box.GetBounds()))
            self.box_widgets.append(box)
            self.classes.append(label["type"])

            box2d = label["box2d"]
            a, b = box2d[1], box2d[3]
            img_size = self.img_style_picker.img_size

            box2d[3] = img_size[1] - a
            box2d[1] = img_size[1] - b

            img_view_port = self.img_style_picker.renderer.GetViewport()
            img_start = img_view_port[:2]
            size = self.interactor.GetRenderWindow().GetSize()

            box2d[1]+=img_start[1] * size[1]
            box2d[3]+=img_start[1] * size[1]

            border_widget = BorderWidget(box2d[:2],
                                         box2d[2:],
                                         img_view_port[:2],
                                         self.img_style_picker.renderer,
                                         self.interactor)

            # border_widget.SetCurrentRenderer(self.img_style_picker.renderer)
            self.img_style_picker.border_widgets.append(border_widget)

    def SetImgStylePicker(self,img_style_picker):
        self.img_style_picker = img_style_picker

        self.AddStylePickerRenderer(img_style_picker)

    def SetPointCloudStylePicker(self,pc_style_picker):
        self.pc_style_picker = pc_style_picker
        # self.pc_style_picker.renderer.SetViewport(self.poly_view_port)
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
        self.Next(save=False)
        super().Start()

    def Next(self,save=True):
        if save:
            self.SaveLabel()

        self.dataset.LoadNext(self.mode)

        self.Reset()

        self.Init()

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
        if not box_widget.selected:
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

    def _ConvertPosToBox(self,start,end):
        size = self.interactor.GetRenderWindow().GetSize()
        new_original = []
        img_start = self.img_view_port[:2]
        new_original.append(img_start[0]*size[0])
        new_original.append(img_start[1]*size[1])
        img_size = self.pc_style_picker.img_size

        # translation of origin
        start[0] -=new_original[0]
        start[1] -=new_original[1]

        end[0] -=new_original[0]
        end[1] -=new_original[1]

        # flip
        start[1] = img_size[1]-start[1]
        end[1] = img_size[1]-end[1]

        return start+end

    def _ConvertBoxToPos(self,start,end):
        size = self.interactor.GetRenderWindow().GetSize()
        new_original = []
        img_start = self.img_view_port[:2]
        new_original.append(img_start[0]*size[0])
        new_original.append(img_start[1]*size[1])
        img_size = self.img_style_picker.img_size

        # flip
        start[1] = img_size[1]-start[1]
        end[1] = img_size[1]-end[1]

        # translation of origin
        end[0] += new_original[0]
        end[1] += new_original[1]

        start[0] += new_original[0]
        start[1] += new_original[1]
        return start+end



    def RegisterDisplayerCallback(self):
        self.callback = DisplayerCallback(self)
