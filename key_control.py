from callback import Callback

class KeyControl(Callback):
    def __init__(self,interactor,debug=False):
        super().__init__(interactor)
        self.key_observer = {}
        self.debug = debug


    def AddKeyObserver(self,key,callback):
        self.key_observer[key] = callback

    def __KeyEventCallback(self,interactor,event):
        key = self.obj.GetKeySym()
        if self.key_observer.get(key):
            self.key_observer[key](interactor,event)
        else:
            if self.debug:
                print("INFO: unregesiter key event")

        self.obj.GetRenderWindow().Render()

    def StartListen(self):
        self.AddObserver("KeyPressEvent",self.__KeyEventCallback)