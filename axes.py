from displayer import Displayer
from utils import SetMapperAndActor
from vtk import vtkAxesActor, vtkInteractorStyleTrackballCamera


def main():
    # SetMapperAndActor()
    axes = vtkAxesActor()
    displayer = Displayer(axes, style=vtkInteractorStyleTrackballCamera())

    displayer.Start()


main()
