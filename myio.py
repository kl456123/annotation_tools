import vtk
import os
from utils import read_from,GeneratePointPolyData,GenerateColors

class ImageReaderFactory(object):
    def __init__(self):
        pass

    def _AnalysisFileType(self,filename):
        return os.path.splitext(filename)[1][1:]

    def GenerateImageReader(self,file_type):

        if file_type=="png":
            png_reader = vtk.vtkPNGReader()

            return png_reader
        elif file_type=="jpg" or file_type=="jpeg":
            jpeg_reader = vtk.vtkJPEGReader()

            return jpeg_reader
        else:
            raise TypeError()
from utils import load_calibration
class PointCloudReader(object):
    def __init__(self,cfg):
        self.transform = cfg["transform"]
        self.color_name = cfg["color"]
        self.calib_path = cfg["calib_path"]
        self.vertexGlyphFilter = vtk.vtkVertexGlyphFilter()
        self.calib = None

    def GetCalibName(self,filename):
        calib_filename =  os.path.splitext(os.path.basename(filename))[0]+".txt"
        return os.path.join(self.calib_path,calib_filename)

    def LoadCalib(self,calib_file):
        self.calib = load_calibration(calib_file)

    def SetFileName(self,filename):
        calib_name = self.GetCalibName(filename)
        self.LoadCalib(calib_name)
        scans = read_from(filename,calib_name,self.transform)
        polydata = GeneratePointPolyData(scans, self.color_name)
        self.vertexGlyphFilter.SetInputData(polydata)


    # def GeneratePointPolyData(self):
    #     scans = read_from(self.filename, self.transform)
    #     # self.scans = scans
    #     polydata = GeneratePointPolyData(scans,self.color_name)
    #     # self.polydata = polydata
    #     # self.colors = polydata.GetPointData().GetScalars()
    #
    #     self.vertexGlyphFilter.SetInputData(polydata)

    def GetOutputPort(self):
        return self.vertexGlyphFilter.GetOutputPort()

    def GetOutput(self):
        return self.vertexGlyphFilter.GetOutput()

    def Update(self):
        self.vertexGlyphFilter.Update()
