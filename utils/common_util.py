# -*- coding: utf-8 -*-

import os
import collections
import vtk


def ListFile(dir_path):
    return [
        f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
    ]


def Update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = Update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def GeneratePointPolyData(scan, color_name="red"):
    numofpoints = scan.shape[0]
    points = vtk.vtkPoints()
    from vtk.util import numpy_support

    points.SetData(numpy_support.numpy_to_vtk(scan[:, :3]))

    pointsPolyData = vtk.vtkPolyData()
    pointsPolyData.SetPoints(points)

    colors = GenerateColors(numofpoints, color_name)

    # set to polydata
    pointsPolyData.GetPointData().SetScalars(colors)

    return pointsPolyData


def GeneratePointPolyFilter(scans, color_name="red"):
    polydata = GeneratePointPolyData(scans, color_name)
    vertexGlyphFilter = vtk.vtkVertexGlyphFilter()
    vertexGlyphFilter.SetInputData(polydata)
    return vertexGlyphFilter


def GenerateColors(num, color_name="green"):
    # set color for each point
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")
    # list some colors
    red = [255, 0, 0]
    green = [0, 255, 0]
    blue = [0, 0, 255]
    if color_name == "red":
        color = red
    elif color_name == "green":
        color = green
    elif color_name == "blue":
        color = blue

    for i in range(num):
        colors.InsertNextTypedTuple(color)
    return colors


def SetMapperAndActor(polydata):
    mapper = vtk.vtkPolyDataMapper()
    if isinstance(polydata, vtk.vtkAlgorithmOutput):
        mapper.SetInputConnection(polydata)
    elif isinstance(polydata, vtk.vtkDataObject):
        mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def GetTruncatedAndOccluded():
    return -1, -1


def GetObserverAngle(box2d):
    return -1


def ConvertNumpy2VTK(ndarray):
    m = vtk.vtkMatrix4x4()
    for i in range(4):
        for j in range(4):
            m.SetElement(i, j, ndarray[i, j])
    return m


def color_map(color_name):
    color_map = {
        "red": [255, 0, 0],
        "green": [0, 255, 0],
        "blue": [0, 0, 255],
        "gray": [88, 88, 88]
    }
    return color_map[color_name]


def mkVtkIdList(it):
    vil = vtk.vtkIdList()

    for i in it:
        vil.InsertNextId(int(i))
    return vil


def GenerateColorMap(num_classes):
    import random
    color_map = []
    for i in range(num_classes):
        color_map.append([random.random() for _ in range(3)])
    return color_map
