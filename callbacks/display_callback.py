# -*- coding: utf-8 -*-

from annotation_tools.callback import Callback
import vtk


class DisplayerCallback(Callback):
    def __init__(self, displayer, debug=False):
        super().__init__(displayer.interactor, debug, displayer.interactor)
        self.displayer = displayer
        self.add_widget = False

    def ToggleDisplayerCurrentBoxWidget(self, obj, event):
        cur = self.displayer.selection.box_widget
        if cur.GetEnabled():
            cur.Off()
        else:
            cur.On()

    def BeforeQuit(self, obj, event):
        self.displayer.dataset.SaveStatus()

    def Start(self):
        self.AddEventObserver(vtk.vtkCommand.MouseMoveEvent,
                              self.LeftButtonPressEvent)

        self.AddKeyObserver("a", self.AddSelectionBoxWidget)
        self.AddKeyObserver("i", self.ToggleDisplayerBoxWidgets)
        self.AddKeyObserver("0", self.SaveLabel)
        self.AddKeyObserver("9", self.PrintLabel)
        self.AddKeyObserver("j", self.ToggleDisplayerCurrentBoxWidget)
        self.AddKeyObserver("k", self.PrevServeral)
        self.AddKeyObserver("l", self.NextSeveral)
        self.AddKeyObserver("m", self.PrevOne)
        self.AddKeyObserver("n", self.NextOne)
        self.AddKeyObserver("r", self.ToggleMode)
        self.AddKeyObserver("q", self.BeforeQuit)

    def ToggleMode(self, obj, event):
        print(self.displayer.pc_style_picker.style.GetEnabled())

    def Prev(self, step):
        # if self.displayer.dataset.data_idx <= 0:
        #     print("it is the first data! ")
        #     return
        if self.displayer.auto_save:
            self.displayer.SaveLabel()
        try:
            self.displayer.dataset.LoadPrev(step)
        except AssertionError as e:
            print("ERROR: ", e)
            return
        self.displayer.Reset()

        self.displayer.Init()

    def PrevOne(self, obj, event):
        self.Prev(1)

    def PrevServeral(self, obj, event):
        self.Prev(self.displayer.dataset.step)

    def Next(self, step):
        """
        process:
        1. save the last label
        2. load next data and label(if have)
        3. reset inner state
        4. init inner state according to the input data
        """

        # save
        if self.displayer.auto_save:
            self.displayer.SaveLabel()

        # next
        try:
            self.displayer.dataset.LoadNext(step=step)
        except AssertionError as e:
            print("ERROR: ", e)
            return
        self.displayer.Reset()

        self.displayer.Init()

    def NextOne(self, obj, event):
        self.Next(1)

    def NextSeveral(self, obj, event):
        self.Next(self.displayer.dataset.step)

    def SaveLabel(self, obj, event):

        self.displayer.SaveLabel()

    def SetLabel(self, obj, event):
        self.displayer.SetLabel()

    def PrintLabel(self, obj, event):
        self.displayer.dataset.PrintLabel()

    def ToggleDisplayerBoxWidgets(self, obj, event):
        # flag = None

        for idx, boxwidget in enumerate(self.displayer.box_widgets):
            if idx == 0:
                flag = boxwidget.GetEnabled()
                boxwidget.SetEnabled(not flag)
            else:
                boxwidget.SetEnabled(not flag)

        # self.displayer.AdjustBoxWidgetsColor()

    def AddSelectionBoxWidget(self, obj, event):
        # add current box widget of selection
        if not self.displayer.selection.IsObjectSelected():
            print("please select object first! ")
            return

        self.displayer.AddBoxWidget()

        self.displayer.InputClass()

        self.displayer.InputOrientation()

        # pass box widget to pc_style_picker
        self.displayer.pc_style_picker.SetCurrentBoxWidget(
            self.displayer.selection.GetCurrentBoxWidget())

        # reset selection box widget
        self.displayer.selection.Reset()

    def LeftButtonPressEvent(self, obj, event):
        xypos = self.interactor.GetEventPosition()
        if self.debug:
            print("Event Position: ", xypos)

        idx = self.displayer.SwitchCondition(xypos)
        self.displayer.SwitchStylePicker(idx)

    def AddBoxWidget(self, obj, event):
        if not self.add_widget:
            return
        pos = self.interactor.GetEventPosition()

    def TriggleAddBoxWidget(self, obj, event):
        if self.add_widget:
            self.add_widget = False
        else:
            self.add_widget = True


