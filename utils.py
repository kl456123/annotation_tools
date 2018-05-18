import numpy as np
import vtk


def CreateBoxCoordsFromCorner(bottomleft,topright):
    topleft = [bottomleft[0],topright[1],0]
    bottomright = [topright[0],bottomleft[1],0]
    return [bottomleft,topleft,topright,bottomright]

def load_calibration(calib_file):
    calib = [x.strip().split() for x in open(calib_file).readlines()]
    P0 = np.array(list(map(float,calib[0][1:]))).reshape((3,4))
    P1 = np.array(list(map(float,calib[1][1:]))).reshape((3,4))
    P2 = np.array(list(map(float,calib[2][1:]))).reshape((3,4))
    P3 = np.array(list(map(float,calib[3][1:]))).reshape((3,4))
    R0_rect = np.eye(4, dtype='float32')
    R0_3x3 = np.array(list(map(float,calib[4][1:]))).reshape((3,3))
    R0_rect[:3,:3] = R0_3x3
    T_v2c = np.eye(4, dtype='float32')
    T_v2c[:3,:] = np.array(list(map(float,calib[5][1:]))).reshape((3,4))
    T_vel_to_cam = np.dot(R0_rect, T_v2c)
    calibs = {'P0': P0, 'P1': P1, 'P2': P2,'P3': P3,
              'R0_rect': R0_rect,
              'T_v2c': T_v2c, 'T_vel_to_cam': T_vel_to_cam}
    return calibs

def mkVtkIdList(it):
    vil = vtk.vtkIdList()

    for i in it:
        vil.InsertNextId(int(i))
    return vil

def read_from(filename,calib_file, transform=False):
    scan = np.fromfile(filename, dtype=np.float32)
    scan = scan.reshape((-1, 4))
    # delete the last column and convert to homo
    scan[:,3] = 1

    # R = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]])
    # scan = scan.dot(R.T)
    # scan = scan[:,:3]
    if not transform:
        return scan
    calib = load_calibration(calib_file)
    extrinsic = calib["T_vel_to_cam"]
    # extrinsic = GetExtrinsicMatrix()
    scan = (extrinsic.dot(scan.T)).T

    # scan = scan.dot(extrinsic.T)
    scan = scan/scan[:,3].reshape((-1,1))
    return scan


def pointtrans3Dto2D(points_3D):
    if not isinstance(points_3D,np.ndarray):
        points_3D = np.array(points_3D)
    assert points_3D.shape[0]==3,print("type of point should be (x,y,z)")

    # convert to homo
    points_3D_h = np.ones((4,))
    points_3D_h[:3]=points_3D

    # transform matrix
    P = transform_matrix3Dto2D()

    points_2D_h = P.dot(points_3D_h)

    # convert back
    points_2D_h = points_2D_h/points_2D_h[2]
    points_2D = points_2D_h[:2]

    return points_2D

def pointtrans2Dto3D(point_2D):
    if not isinstance(point_2D,np.ndarray):
        point_2D = np.array(point_2D)
    assert point_2D.shape[0]==2,print("type of point should be (x,y,z)")
    # convert to homo
    point_2D_h = np.ones((3,))
    point_2D_h[:2]=point_2D

    # transform matrix
    P_inv = transform_matrix2Dto3D()

    point_3D_h = P_inv.dot(point_2D_h)
    # print(point_2D_h*scale)
    # convert back
    point_3D_h = point_3D_h/point_3D_h[3]
    point_3D = point_3D_h[:3]

    P = transform_matrix3Dto2D()

    center = null(P)
    center = center /center[3]
    center = center[:3]
    return  point_3D,center


    return point_3D


def transform_matrix2Dto3D():
    P = transform_matrix3Dto2D()

    return np.linalg.inv(P.T.dot(P)).dot(P.T)

def GetIntrinsicMatrix():
    # (3x4 matrix)
    P_rect_00 = np.array([7.215377e+02, 0.000000e+00, 6.095593e+02, 0.000000e+00,
                          0.000000e+00, 7.215377e+02, 1.728540e+02, 0.000000e+00,
                          0.000000e+00, 0.000000e+00, 1.000000e+00, 0.000000e+00]).reshape((3, 4))
    return P_rect_00


def ConvertNumpy2VTK(ndarray):
    m = vtk.vtkMatrix4x4()
    for i in range(4):
        for j in range(4):
            m.SetElement(i,j,ndarray[i,j])
    return m

def GetExtrinsicMatrix():
    # (4x4 matrix )
    # after rectification
    R = np.array([7.533745e-03, -9.999714e-01, -6.166020e-04,
                  1.480249e-02, 7.280733e-04, -9.998902e-01,
                  9.998621e-01, 7.523790e-03, 1.480755e-02]).reshape((3, 3))

    # translation
    T = np.array([-4.069766e-03, -7.631618e-02, -2.717806e-01])
    R_concat_T = np.zeros((4, 4))
    R_concat_T[:3, :3] = R
    R_concat_T[:3, 3] = T
    R_concat_T[3, 3] = 1
    # return R_concat_T

    R_rect_00 = np.array([9.999239e-01, 9.837760e-03, -7.445048e-03,
                          -9.869795e-03, 9.999421e-01, -4.278459e-03,
                          7.402527e-03, 4.351614e-03, 9.999631e-01]).reshape((3, 3))
    R_rect_00_paded = np.zeros((4, 4))
    R_rect_00_paded[:3, :3] = R_rect_00
    R_rect_00_paded[3, 3] = 1

    return R_rect_00_paded.dot(R_concat_T)

def transform_matrix3Dto2D():
    Extrinsic = GetExtrinsicMatrix()
    Intrinsic = GetIntrinsicMatrix()
    return Intrinsic.dot(Extrinsic)

def DeepCopyPlanes(src):
    planes = vtk.vtkPlanes()
    planes.SetPoints(src.GetPoints())
    planes.SetNormals(src.GetNormals())
    return planes



def SetMapperAndActor(polydata):
    mapper = vtk.vtkPolyDataMapper()
    if isinstance(polydata,vtk.vtkAlgorithmOutput):
        mapper.SetInputConnection(polydata)
    elif isinstance(polydata,vtk.vtkDataObject):
        mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def GeneratePointPolyData(scan, color_name="red"):
    numofpoints = scan.shape[0]
    points = vtk.vtkPoints()
    for k in range(numofpoints):
        point = scan[k, :3]
        points.InsertNextPoint(point)

    pointsPolyData = vtk.vtkPolyData()
    pointsPolyData.SetPoints(points)

    colors = GenerateColors(numofpoints, color_name)

    # set to polydata
    pointsPolyData.GetPointData().SetScalars(colors)

    return pointsPolyData

def GeneratePointPolyFilter(scans,color_name="red"):
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



def GenerateCameraParameter():
    # test pass
    # rotation
    R = np.array([7.533745e-03, -9.999714e-01, -6.166020e-04,
                  1.480249e-02, 7.280733e-04,-9.998902e-01,
                  9.998621e-01, 7.523790e-03, 1.480755e-02]).reshape((3,3))
    # translation
    T = np.array([-4.069766e-03, -7.631618e-02, -2.717806e-01])

    # extrinsic matrix
    E = np.zeros((4, 4))
    E[:3, :3] = R
    E[:3, 3] = T
    E[3, 3] = 1

    E_inv = np.linalg.inv(E)

    view_up = E_inv[:3, 1]
    position = E_inv[:3, 3]
    # the normalized focus to position vector
    normalized = E_inv[:3, 2]

    # distance between focal point and position
    distance = 100
    focal_point = position-normalized*100
    return -view_up,position,focal_point

def GetSlope(point1,point2):
    delta = point2-point1
    return delta[1]/delta[2]

def GetPlaneFromPoint3D(point1_3D,point2_3D,point3_3D):
    plane = vtk.vtkPlane()
    normal =vtk.vtkTriangle.ComputeNormal(point1_3D,point2_3D,point1_3D)
    plane.SetNormal(normal)
    plane.SetOrigin(point1_3D)
    return plane

def GetPlaneFromNormalAndOrigin(normal,origin):
    plane = vtk.vtkPlane()
    plane.SetNormal(normal)
    plane.SetOrigin(origin)
    return plane

def GetPlaneFromPoint2D(point1_2D,point2_2D):
    point1_3D,center1 = pointtrans2Dto3D(point1_2D)
    point2_3D,center2 = pointtrans2Dto3D(point2_2D)
    return GetPlaneFromPoint3D(point1_3D,point2_3D,point3_3D)


def null(A, eps=1e-12):
    import scipy
    from scipy import linalg, matrix
    u, s, vh = scipy.linalg.svd(A)
    padding = max(0,np.shape(A)[1]-np.shape(s)[0])
    null_mask = np.concatenate(((s <= eps), np.ones((padding,),dtype=bool)),axis=0)
    null_space = scipy.compress(null_mask, vh, axis=0)
    return scipy.transpose(null_space)

def GetNormaAndOrigin(plane):
    # plane a,b,c,d
    normal = plane[:3]
    if normal[2]:
        origin = [0,0,-plane[3]/normal[2]]
    elif normal[1]:
        origin =[0,plane[3]/normal[1],0]
    else:
        origin = [plane[3]/normal[0],0,0]
    return normal,origin

def ReversePlane(plane):
    normal = list(plane.GetNormal())
    normal[0]=-normal[0]
    normal[1]=-normal[1]
    normal[2]=-normal[2]
    plane.SetNormal(normal)
def PrintNormal(planes):
    for plane in planes:
        print(plane.GetNormal())

def get_frustum_points_of_box2d( P, box):
    # line : (x1, y1) (x2, y2)
    # Ax+By+C = 0
    # A = y2 - y1
    # B = x1 - x2
    # C = x2*y1 - x1 * y2
    l_left = [box[0], box[1], box[0], box[3]]
    l_top = [box[0], box[1], box[2], box[1]]
    l_right = [box[2], box[1], box[2], box[3]]
    l_bottom = [box[0], box[3], box[2], box[3]]
    bounding_planes = []
    for l in [l_left, l_top, l_right, l_bottom]:
        A = l[3] - l[1]
        B = l[0] - l[2]
        C = l[2] * l[1] - l[0] * l[3]
        plane = np.dot(P.T, np.array([A,B,C]))
        normal,origin = GetNormaAndOrigin(plane)

        bounding_planes.append(GetPlaneFromNormalAndOrigin(normal,origin))
        #print A*l[0]+B*l[1]+C,A*l[2]+B*l[3]+C
        #print A,B,C
        #print plane
    left_plane, top_plane, right_plane, bottom_plane = bounding_planes
    PrintNormal(bounding_planes)
    ReversePlane(left_plane)
    ReversePlane(bottom_plane)
    return bounding_planes
    # bounding_plane_vals = []
    # for plane in bounding_planes:
    #     plane_vals = plane[0] * vel_data_c[:,0] + plane[1] * vel_data_c[:, 1] + plane[2] * vel_data_c[:,2] + plane[3]
    #     bounding_plane_vals.append(plane_vals)
    # left_plane, top_plane, right_plane, bottom_plane = bounding_plane_vals
    # frustum_indices = np.logical_and.reduce((left_plane >=0, right_plane <= 0,
    #                                            bottom_plane >= 0, top_plane <= 0))
    # #vel_data_c_frustum = vel_data_c[intersect_indices, :]
    # return frustum_indices

def GenerateImplicitFunction(bounding_planes):

    planes = vtk.vtkImplicitBoolean()
    planes.SetOperationTypeToIntersection()
    for plane in bounding_planes:
        planes.AddFunction(plane)
    return planes


def GetBoundsCenter(bounds):
    center = [0,0,0]
    center[0]  = (bounds[0]+bounds[1])/2
    center[1] = (bounds[2]+bounds[3])/2
    center[2] = (bounds[4]+bounds[5])/2
    return center

def GetBounds(center,dims):
    min_x = center[0]-dims[0]/2
    max_x = center[0]+dims[0]/2
    min_y = center[1]-dims[1]/2
    max_y = center[1]+dims[1]/2
    min_z = center[2]-dims[2]/2
    max_z = center[2]+dims[2]/2
    return (min_x,max_x,min_y,max_y,min_z,max_z)

def GetTruncatedAndOccluded():
    return -1,-1

def GetObserverAngle(box2d):
    return -1

def GetDistanceFromTwoPoints(point1,point2):
    return np.linalg.norm(point2-point1)

