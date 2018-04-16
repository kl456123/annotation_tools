def parse_kitti_label(label_file):
    lines = open(label_file).readlines()
    lines = map(lambda x: x.strip().split(), lines)
    objs = []
    for l in lines:
        o = {}
        o['type'] = l[0]
        o['truncation'] = float(l[1])
        o['occlusion'] = int(l[2])
        o['alpha'] = float(l[3])
        o['box2d'] = [float(l[4]), float(l[5]), float(l[6]), float(l[7])]
        o['h'] = float(l[8])
        o['w'] = float(l[9])
        o['l'] = float(l[10])
        o['t'] = [float(l[11]), float(l[12]), float(l[13])]
        o['yaw'] = float(l[14])
        objs.append(o)
    return objs

def load_calibration(calib_file):
    calib = map(lambda x: x.strip().split(), open(calib_file).readlines())
    P0 = np.array(map(float,calib[0][1:])).reshape((3,4))
    P1 = np.array(map(float,calib[1][1:])).reshape((3,4))
    P2 = np.array(map(float,calib[2][1:])).reshape((3,4))
    P3 = np.array(map(float,calib[3][1:])).reshape((3,4))
    R0_rect = np.eye(4, dtype='float32')
    R0_3x3 = np.array(map(float,calib[4][1:])).reshape((3,3))
    R0_rect[:3,:3] = R0_3x3
    T_v2c = np.eye(4, dtype='float32')
    T_v2c[:3,:] = np.array(map(float,calib[5][1:])).reshape((3,4))
    T_vel_to_cam = np.dot(R0_rect, T_v2c)
    calibs = {'P0': P0, 'P1': P1, 'P2': P2,'P3': P3,
              'R0_rect': R0_rect,
              'T_v2c': T_v2c, 'T_vel_to_cam': T_vel_to_cam}
    return calibs

def get_data_paths(image_id, data_dir, db):
    #image_id = '006961'
    bin_file = '{}/{}/velodyne/{}.bin'.format(data_dir, db, image_id)
    im_file = '{}/{}/image_2/{}.png'.format(data_dir, db, image_id)
    label_file = '{}/{}/label_2/{}.txt'.format(data_dir, db, image_id)
    calib_file = '{}/{}/calib/{}.txt'.format(data_dir, db, image_id)
    return im_file, label_file, calib_file, bin_file

def project_velo2camera(vel_data, calibs):
    # vel_data_c: col 0: back -> front
    #             col 1: down -> up
    #             col 2: left -> right
    homo_vel_data = np.hstack((vel_data[:,:3],np.ones((vel_data.shape[0],1), dtype='float32')))
    vel_data_c = np.dot(homo_vel_data, calibs['T_vel_to_cam'].T)
    vel_data_c /= vel_data_c[:, -1].reshape((-1,1))
    vel_data_c = np.hstack((vel_data_c[:, :3], vel_data[:, -1].reshape((-1,1))))
    return vel_data_c

def project_velo_camera2image(vel_data_c, calibs):
    homo_vel_data_c = np.hstack((vel_data_c[:, :3], np.ones((vel_data_c.shape[0],1), dtype='float32')))
    vel_data_im = np.dot(homo_vel_data_c, calibs['P2'].T)
    vel_data_im /= vel_data_im[:, -1].reshape((-1, 1))
    vel_data_im = vel_data_im[:, :2]
    return vel_data_im

def load_data(label_file, bin_file, calib_file, velo_sampling=None, velo_positive=False):
    vel_data = np.fromstring(open(bin_file).read(), dtype='float32').reshape((-1, 4))
    if velo_sampling:
        vel_data = vel_data[::velo_sampling,:]
    #vel_data = vel_data[vel_data[:,1]<5,:]
    if velo_positive:
        vel_data = vel_data[vel_data[:,0]>0.1,:]
    #vel_data = vel_data[vel_data[:,2]>-1,:]
    annos = parse_kitti_label(label_file)
    calibs = load_calibration(calib_file)
    # convert velodyne points to camera coords
    vel_data_c = project_velo2camera(vel_data, calibs)
    # convert velodyne points to image coords
    vel_data_im = project_velo_camera2image(vel_data_c, calibs)
    return annos, calibs, vel_data_c, vel_data_im