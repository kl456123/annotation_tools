from vtk import vtkPolyData,vtkCellArray,vtkPoints,vtkFloatArray

class PolygonDrawer(object):
    def __init__(self):
        self.polydata = vtkPolyData()
        self.polys = vtkCellArray()
        self.points = vtkPoints()
        self.scalars = vtkFloatArray()
        # self.last_point = None
        self.last_point_id = None

        self.polydata.SetPoints(self.points)
        self.polydata.SetLines(self.polys)
        self.polydata.GetPointData().SetScalars(self.scalars)

        self.polydata_actor = SetMapperAndActor(self.polydata)

    def draw_polygon(self,points):
        pass

    def InsertCell(self,last_point_id,now_point_id):
        # insert edge
        # if self.last_point:
        self.polys.InsertNextCell(2)
        self.polys.InsertCellPoint(mkVtkIdList([last_point_id,now_point_id]))

    def InsertPoint(self,point):
        now_point_id = self.points.InsertNextPoint(point)
        if self.last_point_id:
            self.InsertCell(self.last_point_id,now_point_id)
        self.last_point_id = now_point_id