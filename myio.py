import vtk
import os
from utils import read_from,GeneratePointPolyData,GenerateColors

class ImageReaderFactory(object):
    def __init__(self):
        pass

    def _AnalysisFileType(self,filename):
        return os.path.splitext(filename)[1][1:]

    def GenerateImageReader(self,filename):
        file_type = self._AnalysisFileType(filename)
        if file_type=="png":
            png_reader = vtk.vtkPNGReader()
            png_reader.SetFileName(filename)
            return png_reader
        elif file_type=="jpg" or file_type=="jpeg":
            jpeg_reader = vtk.vtkJPEGReader()
            jpeg_reader.SetFileName(filename)
            return jpeg_reader
        else:
            raise TypeError()

class PointCloudReader(object):
    def __init__(self,filename,transform=True, color_name="red"):
        self.filename = filename
        self.transform = transform
        self.color_name = color_name

        self.GeneratePointPolyData()

    def GeneratePointPolyData(self):
        scans = read_from(self.filename, self.transform)
        self.scans = scans
        polydata = GeneratePointPolyData(scans,self.color_name)
        # self.polydata = polydata
        # self.colors = polydata.GetPointData().GetScalars()
        self.vertexGlyphFilter = vtk.vtkVertexGlyphFilter()
        self.vertexGlyphFilter.SetInputData(polydata)

    def GetOutputPort(self):
        return self.vertexGlyphFilter.GetOutputPort()

    def GetOutput(self):
        return self.vertexGlyphFilter.GetOutput()
