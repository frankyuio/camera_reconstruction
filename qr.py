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

def __mapAlignmentMarker(markers):
	""" Finds alignment marker using contour area """
	minVal = 0
	minIndex = 0
	for i in range(len(markers)):
		if minVal == 0 or markers[i][2] < minVal:
			minIndex = i
			minVal = markers[i][2]

	A = markers[minIndex] # Alignment marker is the smallest
	del markers[minIndex] # remove alignment marker from unmapped list
	return A

def __mapPositionXMarker (A, markers):
	""" Uses angles between alignment and position markers to find X """
	a1 = np.arctan2(A[1] - markers[0][1], markers[0][0] - A[0])
	a2 = np.arctan2(A[1] - markers[1][1], markers[1][0] - A[0])
	a3 = np.arctan2(A[1] - markers[2][1], markers[2][0] - A[0])

	# Finding the relative internal angles between the three position markers
	a12 = 2 * np.pi - abs(a1 - a2) if abs(a1 - a2) > np.pi else abs(a1 - a2)
	a13 = 2 * np.pi - abs(a1 - a3) if abs(a1 - a3) > np.pi else abs(a1 - a3)
	a23 = 2 * np.pi - abs(a2 - a3) if abs(a2 - a3) > np.pi else abs(a2 - a3)

	# Angle YAZ will be greater than angles XAY and XAZ.
	# Hence X, Y, Z can be determined using angles.
	if abs(a12) > abs(a13) and abs(a12) > abs(a23):
		X = markers[2]
		del markers[2]
	elif abs(a13) > abs(a12) and abs(a13) > abs(a23):
		X = markers[1]
		del markers[1]
	else:
		X = markers[0]
		del markers[0]

	return X

def __mapMarkers(markers):
	"""  Maps markers to X, Y, Z, A """
	A = __mapAlignmentMarker(markers)
	X = __mapPositionXMarker(A, markers)

	# Determining Z and Y from remaining markers
	aX = np.arctan2(A[1] - X[1], X[0] - A[0])
	aX = aX if aX > 0 else aX + 2 * np.pi
	a1 = np.arctan2(A[1] - markers[0][1], markers[0][0] - A[0])
	a1 = a1 if a1 > 0 else a1 + 2 * np.pi

	# YA is clockwise from XA
	diff = aX - a1 if aX - a1 > 0 else aX - a1 + 2 * np.pi
	if diff < np.pi:
		Y = markers[0]
		Z = markers[1]
	else:
		Z = markers[0]
		Y = markers[1]

	# returning marker positions
	return (X[0:2], Y[0:2], Z[0:2], A[0:2])

def findMarkers(img):
	""" Finding and Mapping QR marker coordinates """

	# Detecting contours in the image
	img, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, 
														cv2.CHAIN_APPROX_SIMPLE)

	# Use contour hierarchy to locate the 3 position markers and alignment marker
	markers = []
	for h in hierarchy[0]:
		# After applying threshold, outermost contour (0) is the paper
		# All four markers are contained in contours with non 0 parents
		if h[2] > 0 and h[3] > 0:
			# Appending marker location and size info
			marker = contours[h[2]] # marker is the child of the contour found
			M = cv2.moments(marker)
			cx = int(M['m10']/M['m00']) # marker x coordinate
			cy = int(M['m01']/M['m00']) # marker y coordinate
			area = cv2.contourArea(marker)
			markers.append((cx, cy, area))

	X, Y, Z, A = __mapMarkers(markers)

	return (X, Y, Z, A)