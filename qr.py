# By Frank Yu

import cv2
import numpy as np

"""
Utility functions used to identify markers from QR code image
Assume a QR code is oriented as such where X, Y, Z are position markers and
A is the alignment marker
X----------Y
------------
------------
------------
---------A--
Z-----------
"""

def __map_alignment_marker(markers):
    """ Finds alignment marker using contour area """
    min_val = 0
    min_index = 0
    for i, item in enumerate(markers):
        if min_val == 0 or markers[i][2] < min_val:
            min_index = i
            min_val = markers[i][2]

    align_marker = markers[min_index] # Alignment marker is the smallest
    del markers[min_index] # remove alignment marker from unmapped list
    return align_marker

def __map_position_x_marker(align_marker, markers):
    """ Uses angles between alignment and position markers to find X """
    angle_1 = np.arctan2(align_marker[1] - markers[0][1], markers[0][0] - align_marker[0])
    angle_2 = np.arctan2(align_marker[1] - markers[1][1], markers[1][0] - align_marker[0])
    angle_3 = np.arctan2(align_marker[1] - markers[2][1], markers[2][0] - align_marker[0])

    # Finding the relative internal angles between the three position markers
    a12 = 2 * np.pi - abs(angle_1 - angle_2) if abs(angle_1 - angle_2) > np.pi else abs(angle_1 - angle_2)
    a13 = 2 * np.pi - abs(angle_1 - angle_3) if abs(angle_1 - angle_3) > np.pi else abs(angle_1 - angle_3)
    a23 = 2 * np.pi - abs(angle_2 - angle_3) if abs(angle_2 - angle_3) > np.pi else abs(angle_2 - angle_3)

    # Angle YAZ will be greater than angles XAY and XAZ.
    # Hence X, Y, Z can be determined using angles.
    if abs(a12) > abs(a13) and abs(a12) > abs(a23):
        marker_x = markers[2]
        del markers[2]
    elif abs(a13) > abs(a12) and abs(a13) > abs(a23):
        marker_x = markers[1]
        del markers[1]
    else:
        marker_x = markers[0]
        del markers[0]

    return marker_x

def __map_markers(markers):
    """  Maps markers to X, Y, Z, A """
    align_marker = __map_alignment_marker(markers)
    marker_x = __map_position_x_marker(align_marker, markers)

    # Determining Z and Y from remaining markers
    angle_x = np.arctan2(align_marker[1] - marker_x[1], marker_x[0] - align_marker[0])
    angle_x = angle_x if angle_x > 0 else angle_x + 2 * np.pi
    angle = np.arctan2(align_marker[1] - markers[0][1], markers[0][0] - align_marker[0])
    angle = angle if angle > 0 else angle + 2 * np.pi

    # YA is clockwise from XA
    diff = angle_x - angle if angle_x - angle > 0 else angle_x - angle + 2 * np.pi
    if diff < np.pi:
        marker_y = markers[0]
        marker_z = markers[1]
    else:
        marker_z = markers[0]
        marker_y = markers[1]

    # returning marker positions
    return (marker_x[0:2], marker_y[0:2], marker_z[0:2], align_marker[0:2])

def find_markers(img):
    """ Finding and Mapping QR marker coordinates """

    # Detecting contours in the image
    img, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_SIMPLE)

    # Use contour hierarchy to locate the 3 position markers and alignment marker
    markers = []
    for item in hierarchy[0]:
        # After applying threshold, outermost contour (0) is the paper
        # All four markers are contained in contours with non 0 parents
        if item[2] > 0 and item[3] > 0:
            # Appending marker location and size info
            contour = contours[item[2]] # marker is the child of the contour found
            marker = cv2.moments(contour)
            marker_x = int(marker['m10']/marker['m00']) # marker x coordinate
            marker_y = int(marker['m01']/marker['m00']) # marker y coordinate
            area = cv2.contourArea(contour)
            markers.append((marker_x, marker_y, area))

    marker_x, marker_y, marker_z, align_marker = __map_markers(markers)

    return (marker_x, marker_y, marker_z, align_marker)
