# -*- coding: utf-8 -*-
import numpy as np


def load_calibration(calib_file):
    calib = [x.strip().split() for x in open(calib_file).readlines()]
    P0 = np.array(list(map(float, calib[0][1:]))).reshape((3, 4))
    P1 = np.array(list(map(float, calib[1][1:]))).reshape((3, 4))
    P2 = np.array(list(map(float, calib[2][1:]))).reshape((3, 4))
    P3 = np.array(list(map(float, calib[3][1:]))).reshape((3, 4))
    R0_rect = np.eye(4, dtype='float32')
    R0_3x3 = np.array(list(map(float, calib[4][1:]))).reshape((3, 3))
    R0_rect[:3, :3] = R0_3x3
    T_v2c = np.eye(4, dtype='float32')
    T_v2c[:3, :] = np.array(list(map(float, calib[5][1:]))).reshape((3, 4))
    T_vel_to_cam = np.dot(R0_rect, T_v2c)
    calibs = {
        'P0': P0,
        'P1': P1,
        'P2': P2,
        'P3': P3,
        'R0_rect': R0_rect,
        'T_v2c': T_v2c,
        'T_vel_to_cam': T_vel_to_cam
    }
    return calibs


def read_from(filename, calib_file, transform=False):
    import os
    if os.path.splitext(filename)[1] == '.pkl':
        scan = np.load(filename, encoding='bytes')[b'points']
    else:
        scan = np.fromfile(filename, dtype=np.float32)
    scan = scan.reshape((-1, 4))
    # delete the last column and convert to homo
    scan[:, 3] = 1

    if not transform:
        extrinsic = np.asarray(
            [0, -1, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 1]).reshape((4, 4))
    else:
        calib = load_calibration(calib_file)
        extrinsic = calib["T_vel_to_cam"]
    # extrinsic = GetExtrinsicMatrix()
    scan = (extrinsic.dot(scan.T)).T

    # scan = scan.dot(extrinsic.T)
    scan = scan / scan[:, 3].reshape((-1, 1))
    return scan
