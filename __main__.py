# By Frank Yu

from os import path
import cv2
import numpy as np

import qr
import plot

SCRIPT_DIR = path.dirname(path.realpath(__file__))
IMAGE_PATH = path.join(SCRIPT_DIR, 'images')

# Cycling through images
for i in range(19, 28):
    # Load and preprocess image
    img_path = path.join(IMAGE_PATH, 'IMG_67'+ str(i) + '.JPG')
    img = cv2.imread(img_path, 0)
    img = cv2.resize(img, (612, 816)) # reducing size to minimize computations

    # Applying threshold to bring out paper and QR code from carpet background
    blur = cv2.GaussianBlur(img, (3, 3), 0) # Used to smooth the image
    ret, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    """
    Assume a QR code is oriented as such where X, Y, Z are position markers and
    A is the alignment marker
    X----------Y
    ------------
    ------------
    ------------
    ---------A--
    Z-----------
    """

    # Finding marker locations
    marker_x, marker_y, marker_z, align_marker = qr.find_markers(np.array(otsu, copy=True))

    """
    Defining real world coordinates of QR pattern markers.
    Assume the QR code is resting on the plane Z = 0 with its center on the
    origin. All values were found using photo editing software and are in meters.
    """
    real_x = (-0.024157, 0.024157, 0)
    real_y = (0.024157, 0.024157, 0)
    real_z = (-0.024157, -0.024157, 0)
    real_align = (0.015817, -0.015817, 0)

    img_pnts = np.float32([marker_x, marker_y, marker_z, align_marker])
    real_pnts = np.float32([real_x, real_y, real_z, real_align])

    """
    Creating camera intrinsic matrix (K) based on iphone 6 camera specs found
    online. Image was scaled down by a factor of 4 hence principle point and pixel
    size were scaled accordingly. All real world measurements in meters
    """
    focal = 0.00415
    c_x = 1224 / 4
    c_y = 1632 / 4
    psize_x = 0.0000015 * 4
    psize_y = 0.0000015 * 4

    k_matrix = np.matrix([[focal/psize_x, 0, c_x], [0, focal/psize_y, c_y], [0, 0, 1]])

    # Finding image translation and rotation in terms of camera coordinates
    ret, rvec, tvec = cv2.solvePnP(real_pnts, img_pnts, k_matrix, np.float32([]))

    # Converting camera coordinates to real world coordinates
    r_matrix, d = cv2.Rodrigues(rvec)
    r_matrix = -np.linalg.inv(r_matrix) # Camera rotation matrix
    c_matrix = np.dot(r_matrix, tvec)  # Camera position matrix

    print 'Image: IMG_67'+ str(i) + '.JPG'
    print 'Rotations and displacements are with respect to real world coordinates'
    print 'Displacement in x: {:5.3f} m'.format(c_matrix.item(0))
    print 'Displacement in y: {:5.3f} m'.format(c_matrix.item(1))
    print 'Displacement in z: {:5.3f} m'.format(c_matrix.item(2))

    yaw = np.arctan2(r_matrix[1, 0], r_matrix[0, 0]) + np.pi # z axis is in opposite direction
    yaw = yaw if yaw < np.pi else yaw - 2 * np.pi
    roll = np.arctan2(r_matrix[2, 0], np.sqrt(np.power(r_matrix[2, 1], 2)
                                              + np.power(r_matrix[2, 2], 2)))
    pitch = np.arctan2(r_matrix[2, 1], r_matrix[2, 2])

    print 'Rotation along x (pitch): {:6.3f} degrees'.format(pitch * 180 / np.pi)
    print 'Rotation along y (roll): {:6.3f} degrees'.format(roll * 180 / np.pi)
    print 'Rotation along z (yaw): {:6.3f} degrees'.format(yaw * 180 / np.pi)

    if i < 27:
        print '\nClose plot to move onto next image\n'

    # Showcasing processed image with markers labeled along with 3D plot
    otsu = cv2.circle(otsu, marker_x, 1, (255, 255, 255), 3)
    otsu = cv2.circle(otsu, marker_y, 1, (150, 150, 150), 3)
    otsu = cv2.circle(otsu, marker_z, 1, (60, 60, 60), 3)
    otsu = cv2.circle(otsu, align_marker, 1, (127, 127, 127), 3)

    cv2.imshow('image', otsu)
    plot.show_camera(r_matrix, c_matrix)
