from abc import ABC, abstractclassmethod
import vtk


class Callback(ABC):
    def __init__(self, obj, debug=False, interactor=None):
        self.obj = obj
        self.key_observer = {}
        self.debug = debug
        self.interactor = interactor
        # add key event observer
        if self.interactor:
            # self.interactor.RemoveObserver("KeyPressEvent")
            self.interactor.AddObserver(vtk.vtkCommand.KeyPressEvent,
                                        self.KeyPressEvent, 1.0)

        self.Start()

    def AddEventObserver(self, event, func, priority=1.0):
        self.obj.AddObserver(event, func, priority)

    def AddKeyObserver(self, key, func):
        self.key_observer[key] = func

    @abstractclassmethod
    def Start(self):
        pass

    def KeyPressEvent(self, obj, event):
        if self.interactor is None:
            raise Exception("interactor should be determined first!")

        key = self.interactor.GetKeySym()
        if self.key_observer.get(key):
            self.key_observer[key](self.interactor, event)
        else:
            if self.debug:
                print("INFO: unregesiter key event: ", key)

        self.interactor.GetRenderWindow().Render()


class PickerCallback(Callback):
    def __init__(self, picker, interactor, debug=True):
        super().__init__(picker, debug, interactor)


class StyleCallback(Callback):
    def __init__(self, obj, debug=False, interactor=None):
        super().__init__(obj, debug, interactor)
