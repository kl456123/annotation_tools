import vtk
import math
from abc import ABC, abstractclassmethod

from annotation_tools.core.actor import PolyDataActor, ImageActor
from annotation_tools.core.renderer import Renderer
from annotation_tools.callbacks.display_callback import DisplayerCallback
from annotation_tools.core.box_widget import BoxWidget
from annotation_tools.core.border_widget import BorderWidget
from annotation_tools.core.selection import Selection
from annotation_tools.core.pc_style_picker_renderer import PolyDataStylePickerRenderer
from annotation_tools.core.image_style_picker_renderer import ImageStylePickerRenderer
from annotation_tools.utils.geometry_util import GetBoundsCenter
from annotation_tools.utils.common_util import GetTruncatedAndOccluded, GetObserverAngle, GenerateColorMap
from annotation_tools.core.render_window import RenderWindow


class Displayer(ABC):
    def __init__(self):

        self.SetWindow()

        self.SetInteractor()

        self.RegisterDisplayerCallback()

    def AddRenderer(self, renderer):
        if renderer:
            self.window.AddRenderer(renderer)

    def SetWindow(self):
        self.window = vtk.vtkRenderWindow()

    def SetDataSet(self, dataset):
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
    def __init__(self, dataset, cfg):
        super().__init__()
        self.current_renderer = None
        self.img_style_picker = None
        self.pc_style_picker = None
        self.current_idx = None
        self.StylePickerRenderers = []
        self.auto_save = cfg["auto_save"]
        self.mode = cfg["mode"]
        self.fix_display = self.mode == 'display'
        self.window.SetSize(cfg["window_size"])
        self.window.window_size = tuple(cfg["window_size"])
        self.img_style_flag = False

        # set in order
        self.SetDataSet(dataset)
        self.classes_colors_map = GenerateColorMap(self.dataset.num_classes)
        self.velo_only = self.dataset.velo_only
        self.SetUpPCStylePickerRenderer(cfg["pc"])
        self.SetUpSelection(cfg["selection"])
        if not self.dataset.velo_only:
            self.SetUpImgStylePickerRenderer(cfg["img"])

        #########################################
        # Callback here
        ########################################
        self.window.RegisterRenderWindowCallback(self)

    def SetWindow(self):
        self.window = RenderWindow()

    def SetUpSelection(self, selection_cfg):
        # build selection
        selection = Selection(
            self.dataset.pc_reader.GetFilter(),
            displayer=self,
            point_renderer=self.pc_style_picker.renderer,
            debug=selection_cfg["debug"],
            velo_only=self.dataset.velo_only)
        self.SetSelection(selection)

    def SetUpImgStylePickerRenderer(self, img_cfg):
        # build img style picker renderer
        view_port = img_cfg["view_port"]
        bg = img_cfg["bg"]

        # build renderer and actor
        img_renderer = Renderer()

        img_actor = ImageActor(self.dataset.img_reader.GetOutputPort())
        img_renderer.AddMyActor(img_actor)

        img_style_picker = ImageStylePickerRenderer(img_renderer,
                                                    self.selection)

        # register callback for img_style_picker
        img_style_picker.RegisterStyleCallback(self,
                                               [view_port[0], view_port[1]])
        img_style_picker.renderer.SetViewport(view_port)
        img_style_picker.renderer.SetBackground(bg)

        # shared with pc_style_picker_renderer
        img_style_picker.classes = self.pc_style_picker.classes

        self.SetImgStylePicker(img_style_picker)

    def SetUpPCStylePickerRenderer(self, pc_cfg):
        # build pc style picker renderer

        # actor
        points_actor = PolyDataActor(self.dataset.pc_reader.GetFilter())

        # renderer
        point_renderer = Renderer([points_actor])

        # register callback for point renderer
        point_renderer.camera.in_velo = True if self.dataset.velo_only else False
        point_renderer.RegisterCameraCallback(self)

        # pc_style_picker
        pc_style_picker = PolyDataStylePickerRenderer(point_renderer)

        # set points_actor in pc_style_picker
        pc_style_picker.SetPointsActor(points_actor)

        # pc_style_picker
        pc_style_picker.RegisterPickerCallback(self)
        pc_style_picker.RegisterStyleCallback(self)

        view_port = pc_cfg["view_port"]

        pc_style_picker.renderer.SetViewport(view_port)

        self.SetPointCloudStylePicker(pc_style_picker)

    def Reset(self):
        self.img_style_picker.Reset()
        self.pc_style_picker.Reset()

    def AdjustMode(self):
        if self.fix_display:
            return
        if (self._data_idx - 1) % self.step == 0:
            self.mode = "annotation"
        else:
            self.mode = "display"

    def Init(self):
        # init parameters according to loaded data

        # init window title
        self.Render()
        self.AdjustMode()
        self.SetWindowName()
        if not self.dataset.velo_only:
            self.img_style_picker.SetImageSize(self.dataset.GetImageSize())
        self.AddLabelWidgets(self.dataset.label)

    def SetLabel(self):
        all_info = []
        if self.img_style_picker:
            box_2D = self.img_style_picker.border_widgets
        for idx, box_3D in enumerate(self.pc_style_picker.box_widgets):
            # the num is 16 in all
            info = []
            # 1
            info.append(self.pc_style_picker.classes[idx])
            # 2
            info.extend(GetTruncatedAndOccluded())
            # 1
            info.append(GetObserverAngle(box_3D))
            # 4
            if self.img_style_picker:
                info.extend(box_2D[idx].GetInfo(self.dataset.GetImageSize()))
            else:
                info.extend([-1, -1, -1, -1])
            # 7
            info.extend(box_3D.GetInfo())

            all_info.append(info)

        self.dataset.SetLabel(all_info)
        print("INFO:Save Label success! ")

        self.dataset.SaveStatus()

    def SaveLabel(self):
        # if self.auto_save:
        # save to list(in memory not in disk)
        if self.mode == "display":
            print("WARN: you should not save label in display mode! Turn off "
                  "auto save to swallow this warning")
        elif self.mode == "annotation":
            self.SetLabel()

            # in disk
            self.dataset.SaveLabel()
        else:
            raise ValueError("mode is not recognized!")

    def BindStylePickers(self):
        for border_widget, box_widget in zip(
                self.img_style_picker.border_widgets,
                self.pc_style_picker.box_widgets):
            border_widget.BindBoxWidget(box_widget)

    def AddLabelWidgets(self, labels):
        self.img_style_picker.AddBorderWidgetFromLabel(labels, self)
        self.pc_style_picker.AddBoxWidgetFromLabel(labels, self)

        # bind two style_picker
        if not self.dataset.velo_only:
            self.BindStylePickers()

    def SetColorForBoxWidget(self, box_widget, class_type):
        try:
            class_idx = int(class_type)
        except ValueError:
            # guess class_type is a string of name
            # map it to class_idx
            try:
                class_idx = self.dataset._classes.index(class_type)
            except ValueError:
                # so it is not in classes list,set it default value
                class_idx = -1
        if class_idx == -1:
            box_widget.UnchangeColor()
        else:
            box_widget.SetColor(self.classes_colors_map[class_idx])

    def SetImgStylePicker(self, img_style_picker):
        self.img_style_picker = img_style_picker

        self.AddStylePickerRenderer(img_style_picker)

    def SetPointCloudStylePicker(self, pc_style_picker):
        self.pc_style_picker = pc_style_picker
        # self.pc_style_picker.renderer.SetViewport(self.poly_view_port)
        self.AddStylePickerRenderer(pc_style_picker)

    def InputClass(self):
        class_idx = input("please input index of classes:")
        self.pc_style_picker.classes.append(class_idx)
        self.SetColorForBoxWidget(self.pc_style_picker.box_widgets[-1],
                                  class_idx)

    def InputOrientation(self):
        orientation_idx = input("please input index of plane:")
        self.pc_style_picker.box_widgets[-1].orientation = int(orientation_idx)

    def SetWindowName(self):
        if self.dataset.prefix_name:
            title = "{} :{}".format(self.dataset.cur_prefix_name,
                                    self.pc_style_picker.style_callback.mode)
        else:
            title = "filename:{} (the {}th):{}".format(
                self.dataset.cur_prefix_name, str(self.dataset.data_idx),
                self.pc_style_picker.style_callback.mode)
        title += "                    {}".format(self.mode)
        self.window.SetWindowName(title)

    def Start(self):
        self.Next(save=False)
        super().Start()

    def Next(self, save=True):
        if save:
            self.SaveLabel()

        self.dataset.LoadNext(0)

        self.Reset()

        self.Init()

    def GetWidgetIdx(self):
        if not self.dataset.velodyne_only:
            return self.img_style_picker.border_widgets_idx

    def SetSelection(self, selection):
        self.selection = selection

    def AddStylePickerRenderer(self, stylePickerRenderer):
        self.StylePickerRenderers.append(stylePickerRenderer)
        self.window.AddRenderer(stylePickerRenderer.renderer)

    def GetPointCloudRenderer(self):
        return self.pc_style_picker.renderer

    def AddBoxWidget(self):
        box_widget = self.selection.GetCurrentBoxWidget()

        if not self.selection.IsObjectSelected():
            print("please select first")
            return

        self.pc_style_picker.box_widgets.append(box_widget)

        # add possible focal point to renderer
        point_renderer = self.pc_style_picker
        point_renderer.renderer.AddPossibleFocalPoint(
            GetBoundsCenter(box_widget.GetBounds()))

    def SwitchStylePicker(self, idx):
        if self.current_idx == idx:
            return
        stylePickerRenderer = self.StylePickerRenderers[idx]
        self.current_renderer = stylePickerRenderer.renderer

        picker = stylePickerRenderer.picker
        style = stylePickerRenderer.style
        if picker:
            self.interactor.SetPicker(picker)
        if style:
            self.interactor.SetInteractorStyle(style)

    def _CheckInSide(self, pos, region):
        x, y = pos
        if region[0] <= x and region[2] > x and region[1] <= y and region[3] > y:
            return True
        return False

    def SwitchCondition(self, pos):
        for idx, stylePickerRenderer in enumerate(self.StylePickerRenderers):
            region = list(stylePickerRenderer.renderer.GetViewport())
            size = self.interactor.GetRenderWindow().GetSize()
            region[0] *= size[0]
            region[1] *= size[1]
            region[2] *= size[0]
            region[3] *= size[1]
            if self._CheckInSide(pos, region):
                return idx

    def _ConvertPosToBox(self, start, end):
        size = self.interactor.GetRenderWindow().GetSize()
        new_original = []
        img_start = self.img_view_port[:2]
        new_original.append(img_start[0] * size[0])
        new_original.append(img_start[1] * size[1])
        img_size = self.pc_style_picker.img_size

        # translation of origin
        start[0] -= new_original[0]
        start[1] -= new_original[1]

        end[0] -= new_original[0]
        end[1] -= new_original[1]

        # flip
        start[1] = img_size[1] - start[1]
        end[1] = img_size[1] - end[1]

        return start + end

    def _ConvertBoxToPos(self, start, end):
        size = self.interactor.GetRenderWindow().GetSize()
        new_original = []
        img_start = self.img_view_port[:2]
        new_original.append(img_start[0] * size[0])
        new_original.append(img_start[1] * size[1])
        img_size = self.img_style_picker.img_size

        # flip
        start[1] = img_size[1] - start[1]
        end[1] = img_size[1] - end[1]

        # translation of origin
        end[0] += new_original[0]
        end[1] += new_original[1]

        start[0] += new_original[0]
        start[1] += new_original[1]
        return start + end

    def RegisterDisplayerCallback(self):
        self.callback = DisplayerCallback(self)
