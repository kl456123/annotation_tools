
import vtk
from callback import Callback

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        super().__init__()
        self.polygon_drawer = None

    def SetPolyDataDrawer(self,polygon_drawer):
        self.polygon_drawer = polygon_drawer

    def OnLeftButtonDown(self,obj,event):
        position = self.GetInteractor().GetEventPosition()
        print("Picking pixel: ", position)
        self.GetInteractor().GetPicker().Pick(position[0],position[1],0,self.GetDefaultRenderer())

        picked = self.GetInteractor().GetPicker().GetPickPosition()
        print(picked)

        # insert current position
        if self.polygon_drawer:
            self.polygon_drawer.InsertPoint(picked)
            self.GetInteractor().GetRenderWindow().Render()


class MyStyleCallBack(Callback):
    def __init__(self,style,actor,displayer):
        super().__init__(style)
        self.actor = actor
        self.displayer = displayer

    def EndInteractionEvent(self,style,event):

        # note that the origin of coordinate system is in the left bottom corner
        box = []
        start_pos = list(self.obj.GetStartPosition())
        start_pos[1] = 300-start_pos[1]
        end_pos = list(self.obj.GetEndPosition())
        end_pos[1] = 300 - end_pos[1]
        box+=start_pos
        box+=end_pos
        self.actor.ColorInsideFrustum(box)
        self.displayer.AddActor(self.actor.actor)
        self.displayer.Render()

    def StartListen(self):
        self.AddObserver("EndInteractionEvent",self.EndInteractionEvent)