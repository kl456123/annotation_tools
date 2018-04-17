from abc import ABCMeta,abstractclassmethod
from utils import *
from box_widget import *
import pickle

class Callback(object):
    __metaclass__ = ABCMeta

    def __init__(self,obj,debug=False,interactor=None):
        self.obj = obj
        self.key_observer = {}
        self.debug = debug
        self.interactor = interactor
        # add key event observer
        if self.interactor:
            self.interactor.AddObserver("KeyPressEvent", self.KeyPressEvent)

        self.Start()

    def AddEventObserver(self,event,func):
        self.obj.AddObserver(event,func)

    def AddKeyObserver(self,key,func):
        self.key_observer[key] = func


    @abstractclassmethod
    def Start(self):
        pass

    def KeyPressEvent(self,obj,event):
        if self.interactor is None:
            raise Exception("interactor should be determined first!")

        key = self.interactor.GetKeySym()
        if self.key_observer.get(key):
            self.key_observer[key](self.interactor, event)
        else:
            if self.debug:
                print("INFO: unregesiter key event: ",key)

        self.interactor.GetRenderWindow().Render()


class PickerCallback(Callback):
    __metaclass__ = ABCMeta
    def __init__(self,picker,interactor,debug=True):
        super().__init__(picker,debug,interactor)


class ImagePickerCallback(PickerCallback):
    def __init__(self,picker):
        super().__init__(picker)

    def Start(self):
        pass

class AreaPickerCallback(PickerCallback):
    def __init__(self,picker,displayer,selection):
        super().__init__(picker,interactor=displayer.interactor)
        self.displayer = displayer
        self.selection = selection

    def EndPickEvent(self,obj,event):
        # fix bug (have to use deep copy here)
        frustum = DeepCopyPlanes(self.obj.GetFrustum())

        self.selection.AddFilter(frustum)


        # color it
        self.selection.Color()

        # render again
        self.displayer.Render()

    def SelectionContinueOff(self,obj,event):
        self.selection.SetContinue(False)

    def SelectionContinueOn(self,obj,event):
        self.selection.SetContinue(True)

    def Start(self):
        # add key observer
        self.AddKeyObserver("c",self.SelectionContinueOn)
        self.AddKeyObserver("s",self.SelectionContinueOff)

        # add event observer
        self.AddEventObserver("EndPickEvent",self.EndPickEvent)


class StyleCallback(Callback):
    def __init__(self,obj,debug=False,interactor=None):
        super().__init__(obj,debug,interactor)


class ImageStyleCallback(StyleCallback):
    def __init__(self,obj,style_picker_renderer, displayer=None,selection=None,myactor=None,img_start=[0,0],debug=False):
        super().__init__(obj,debug,displayer.interactor)
        self.displayer = displayer
        self.myactor = myactor
        self.img_start = img_start
        self.selection = selection
        self.style_picker_renderer = style_picker_renderer

    def _ConvertPosToBox(self,start,end):
        size = self.displayer.interactor.GetRenderWindow().GetSize()
        new_original = []
        new_original.append(self.img_start[0]*size[0])
        new_original.append(self.img_start[1]*size[1])
        img_size = self.style_picker_renderer.img_size

        # translation of origin
        start[0] -=new_original[0]
        start[1] -=new_original[1]

        end[0] -=new_original[0]
        end[1] -=new_original[1]

        # flip
        start[1] = img_size[1]-start[1]
        end[1] = img_size[1]-end[1]

        return start+end

    def GenerateImplicifFunction(self,box):
        P = self.displayer.dataset.pc_reader.calib["P2"]
        planes = get_frustum_points_of_box2d(P,box)
        return GenerateImplicitFunction(planes)

    def SelectionChangedEvent(self,obj,event):
        # pass
        start = list(self.obj.GetStartPosition())
        end = list(self.obj.GetEndPosition())
        print("press start end: ",start,end)
        ######################################
        #####generate box in 2D image#########
        border_widget = BorderWidget(start,end,self.img_start,self.displayer.interactor)
        # border_widget.SetRenderer(self.style_picker_renderer.renderer)
        self.style_picker_renderer.border_widgets.append(border_widget)

        box = self._ConvertPosToBox(start,end)
        # print(box)
        planes = self.GenerateImplicifFunction(box)

        self.selection.AddFilter(planes)

        # color it
        self.selection.Color()

        # set continue for selection for convenience
        self.selection.SetContinue(True)

        # render again
        self.displayer.Render()

    def ToggleWidgetProcess(self,obj,event):
        flag = self.style_picker_renderer.border_widgets[0].GetProcessEvents()
        for idx ,border_widget in enumerate(self.style_picker_renderer.border_widgets):
            # if idx==0:
            #     flag = border_widget.GetProcessEvents()
            if flag:
                border_widget.ProcessEventsOff()
            else:
                border_widget.ProcessEventsOn()

    def Reset(self,obj,event):
        current_box = self.style_picker_renderer.border_widgets[-1]
        current_box.Off()
        del current_box

    def Start(self):
        # pass
        self.AddEventObserver("SelectionChangedEvent",self.SelectionChangedEvent)
        self.AddKeyObserver("o",self.ToggleWidgetProcess)
        self.AddKeyObserver("4",self.Reset)

class PointCloudStyleCallback(StyleCallback):
    def __init__(self,obj,debug=False,interactor=None):
        super().__init__(obj,debug,interactor)

    def Start(self):
        pass




class DisplayerCallback(Callback):
    def __init__(self,displayer ,debug=False):
        super().__init__(displayer.interactor,debug,displayer.interactor)
        self.displayer  = displayer
        self.add_widget = False

    def ToggleDisplayerCurrentBoxWidget(self,obj,event):
        cur = self.displayer.selection.box_widget
        if cur.GetEnabled():
            cur.Off()
        else:
            cur.On()

    def Start(self):
        self.AddEventObserver("MouseMoveEvent",self.LeftButtonPressEvent)

        self.AddKeyObserver("a",self.AddSelectionBoxWidget)
        self.AddKeyObserver("i",self.ToggleDisplayerBoxWidgets)
        self.AddKeyObserver("0",self.SetLabel)
        self.AddKeyObserver("9",self.PrintLabel)
        self.AddKeyObserver("n",self.Next)
        self.AddKeyObserver("j",self.ToggleDisplayerCurrentBoxWidget)

    def Next(self,obj,event):
        # save the last label

        if self.displayer.auto_save:
            self.SetLabel(None,None)
        self.displayer.dataset.SaveLabel()

        # next
        self.displayer.dataset.LoadNext()

        self.displayer.SetWindowName()

        self.displayer.img_style_picker.SetImageSize(self.displayer.dataset.GetImageSize())

        # Off all the last box widgets
        self.displayer.CloseLastBoxWidget()
        self.displayer.classes = []
        # self.orientation = []

        self.displayer.img_style_picker.IncreaseIdx()

    def SetLabel(self,obj,event):

        all_info = []
        box_2D = self.displayer.img_style_picker.border_widgets
        for idx, box_3D in  enumerate(self.displayer.box_widgets):
            # the num is 16 in all
            info = []
            # 1
            info.append(self.displayer.classes[idx])
            # 2
            info.extend(GetTruncatedAndOccluded())
            # 1
            info.append(GetObserverAngle(box_3D))
            # 4
            info.extend(box_2D[idx].GetInfo(self.displayer.dataset.GetImageSize()))
            # 7
            info.extend(box_3D.GetInfo())

            # fake score
            # 1
            # info.extend([1.0])

            all_info.append(info)

        self.displayer.dataset.SetLabel(all_info)
        print("INFO:Save Label success! ")


        self.displayer.dataset.SaveStatus()

    def PrintLabel(self,obj,event):
        self.displayer.dataset.PrintLabel()


    def ToggleDisplayerBoxWidgets(self,obj,event):
        flag = None
        widget_idx = self.displayer.GetWidgetIdx()
        print("widget idx: ",widget_idx)
        for idx,boxwidget in enumerate(self.displayer.box_widgets[widget_idx:]):
            if idx==0:
                flag = boxwidget.GetEnabled()
                continue
            boxwidget.SetEnabled(not flag)

    def AddSelectionBoxWidget(self,obj,event):
        # add current box widget of selection
        self.displayer.AddBoxWidget()

        self.displayer.InputClass()

        self.displayer.InputOrientation()
        # self.displayer.AddMyActor(self.displayer.selection.selected_actor)

        # reset selection box widget
        self.displayer.selection.Reset()


    def LeftButtonPressEvent(self,obj,event):
        xypos = self.interactor.GetEventPosition()
        if self.debug:
            print("Event Position: ",xypos)

        idx = self.displayer.SwitchCondition(xypos)
        self.displayer.SwitchStylePicker(idx)

    def AddBoxWidget(self,obj,event):
        if not self.add_widget:
            return
        pos = self.interactor.GetEventPosition()


    def TriggleAddBoxWidget(self,obj,event):
        if self.add_widget:
            self.add_widget=False
        else:
            self.add_widget = True



class CameraCallback(Callback):
    def __init__(self,camera,interactor):
        super().__init__(camera,interactor=interactor)
        self.position = None
        self.focal_point = [0,0,0 ]
        self.viewup = None
        # init fps
        self.possible_fps = [(0,0,0)]
        self.idx_fps = 0
        self.high = 0.1
        self.lower_step = 10
        self.clipping_range = [self.high,100000]

    def LowerSlice(self,obj,event):
        self.high+=self.lower_step
        self.clipping_range[0] = self.high
        self.SetCamera()

    def HigherSlice(self,obj,event):
        self.high-=self.lower_step
        self.clipping_range[0] = self.high
        self.SetCamera()

    def AddPossibleFocalPoint(self,possible_focalpoint):
        self.possible_fps.append(possible_focalpoint)

    def ResetPossibleFocalPoint(self,obj,event):
        self.possible_fps = [(0,0,0)]

    def SwitchFocalPoint(self,obj,event):
        self.idx_fps =(self.idx_fps+1)%len(self.possible_fps)
        self.focal_point = self.possible_fps[self.idx_fps]
        self.SetCamera()

    def RightRotation(self,obj,event):
        self.obj.Azimuth(1)

    def LeftRotation(self,obj,event):
        self.obj.Azimuth(-1)

    def UpRotation(self,obj,event):
        self.obj.Elevation(1)

    def ClockwiseRollRotation(self,obj,event):
        self.obj.Roll(1)

    def CounterclockwiseRollRotation(self,obj,event):
        self.obj.Roll(-1)

    def DownRotation(self,obj,event):
        self.obj.Elevation(-1)

    def SetHorizontalView(self,obj,event):
        self.position = [self.focal_point[0],self.focal_point[1],-100]
        # self.focal_point = [0,0,0]
        self.viewup = [0,-1,0]
        self.SetCamera()

    def PrintCamera(self,interactor,event):
        print(self.obj)

    def SetVerticalView(self,obj , event):
        self.position = [self.focal_point[0],-100,self.focal_point[2]]
        # self.focal_point = [0,0,0]
        self.viewup = [-1,0,0]
        self.SetCamera()

    def ResetCameraView(self,obj,event):
        self.SetVerticalView(obj,event)

    def SetCamera(self):
        self.obj.SetPosition(self.position)
        self.obj.SetFocalPoint(self.focal_point)
        self.obj.SetViewUp(self.viewup)
        self.obj.SetClippingRange(self.clipping_range)

    def Start(self):
        self.AddKeyObserver("v",self.SetVerticalView)
        self.AddKeyObserver("h",self.SetHorizontalView)
        self.AddKeyObserver("p",self.PrintCamera)
        self.AddKeyObserver("Right",self.RightRotation)
        self.AddKeyObserver("Left",self.LeftRotation)
        self.AddKeyObserver("Down",self.DownRotation)
        self.AddKeyObserver("Up",self.UpRotation)
        self.AddKeyObserver("Tab",self.SwitchFocalPoint)
        # self.AddKeyObserver("n",self.ClockwiseRollRotation)
        # self.AddKeyObserver("m",self.CounterclockwiseRollRotation)
        self.AddKeyObserver("1",self.LowerSlice)
        self.AddKeyObserver("2",self.HigherSlice)
        self.AddKeyObserver("n",self.ResetPossibleFocalPoint)

# class BoxWidgetCallback(Callback):
#     def __init__(self,obj,interactor):
#         super(BoxWidgetCallback, self).__init__(obj,interactor=interactor)
#
#     def ColorInsidePoints():
#         print(selectEnclosedPoints.GetOutput())
#         # newcolors = colors.
#         for i in range(numofpoints):
#             if selectEnclosedPoints.IsInside(i):
#                 print("Color")
#                 colors.SetTypedTuple(i, blue)
#             else:
#                 colors.SetTypedTuple(i, red)
#                 # colors[i] = green
#         # pointsPolyData.GetPointData().SetScalars(colors)
#
#     def UnColorInsidePoints():
#         for i in range(numofpoints):
#             print("UnColor")
#             colors.SetTypedTuple(i, red)
#
#     def EndInteractionEvent(self,obj,event):
#         pass

    #
    # def Start(self):
    #     self.AddEventObserver("EndInteractionEvent",self.EndInteractionEvent)

class SelectionCallback(Callback):
    def __init__(self,selection,debug=False):
        super().__init__(selection,debug,selection.displayer.interactor)

        # inner variable
        self.transform = vtk.vtkTransform()
        self.transform.PostMultiply()
        self.angle = 0
        self.angle_step = 1

    def SetBoxCenterFocalPoint(self,obj,event):
        # switch focal point to center of box
        box_widget = self.obj.GetCurrentBoxWidget()
        center = GetBoundsCenter(box_widget.GetBounds())
        renderer = self.obj.displayer.GetPointCloudRenderer()
        renderer.SetFocalPoint(center)

    def ClockwiseRotate(self,obj,event):
        self.angle_step = 1
        self.RotateBoxWidget()

    def CounterclockwiseRotate(self,obj,event):
        self.angle_step = -1
        self.RotateBoxWidget()

    # def TestAdd(self,obj,event):
    #     print("adsga")

    def RotateBoxWidget(self):
        box_widget = self.obj.GetCurrentBoxWidget()
        # center, dims = box_widget.GetCenterAndDims()
        #         # print("center: ",center)
        self.angle += self.angle_step
        # box_widget.SetCenterAndDim(center,dims,self.angle)
        self.transform.Identity()
        #
        center = GetBoundsCenter(box_widget.GetBounds())
        #
        # print("center: ",center)
        # # translation
        self.transform.Translate([-center[0],-center[1],-center[2]])
        #
        # # rotation
        #
        self.transform.RotateY(self.angle)
        # self.transform.Scale()
        box_widget.SetAngle(self.angle)
        #
        # # translation back
        self.transform.Translate(center)
        #
        box_widget.SetTransform(self.transform)

    def Reset(self,obj,event):
        self.obj.Reset()

    def Start(self):
        self.AddKeyObserver("z",self.ClockwiseRotate)
        self.AddKeyObserver("x", self.CounterclockwiseRotate)
        self.AddKeyObserver("b",self.SetBoxCenterFocalPoint)
        self.AddKeyObserver("4",self.Reset)
        # self.AddKeyObserver("a",self.TestAdd)