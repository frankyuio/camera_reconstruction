# By Frank Yu

import cv2
import numpy as np
from os import path

import qr
import plot

# Cycling through images
for i in range (19, 28):
	# Load and preprocess image
	img_path = path.join('images', 'IMG_67'+ str(i) + '.JPG')
	img = cv2.imread(img_path, 0)
	img = cv2.resize(img, (612, 816)) # reducing size to minimize computations

	# Applying threshold to bring out paper and QR code from carpet background
	blur = cv2.GaussianBlur(img, (3, 3), 0) # Used to smooth the image
	ret, img = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

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
	X, Y, Z, A = qr.findMarkers(img)

	"""
	Defining real world coordinates of QR pattern markers.
	Assume the QR code is resting on the plane Z = 0 with its center on the 
	origin. All values were found using photo editing software and are in meters.
	"""
	X1 = (-0.024157, 0.024157, 0)
	Y1 = (0.024157, 0.024157, 0)
	Z1 = (-0.024157, -0.024157, 0)
	A1 = (0.015817, -0.015817, 0)

	img_pnts = np.float32([X, Y, Z, A])
	real_pnts = np.float32([X1, Y1, Z1, A1])

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

	K = np.matrix([[focal/psize_x, 0, c_x], [0, focal/psize_y, c_y], [0, 0, 1]])

	# Finding image translation and rotation in terms of camera coordinates
	ret, rvec, tvec = cv2.solvePnP(real_pnts, img_pnts, K, np.float32([]))

	# Converting camera coordinates to real world coordinates
	R , d = cv2.Rodrigues(rvec)
	R = -np.linalg.inv(R)
	C = np.dot(R, tvec)

	print('Image: IMG_67'+ str(i) + '.JPG')
	print('Rotations and displacements are with respect to real world coordinates')
	print('Displacement in x: {:5.3f} m'.format(C.item(0)))
	print('Displacement in y: {:5.3f} m'.format(C.item(1)))
	print('Displacement in z: {:5.3f} m'.format(C.item(2)))

	yaw = np.arctan2(R[1, 0], R[0, 0]) + np.pi # z axis is in opposite direction
	yaw = yaw if yaw < np.pi else yaw - 2 * np.pi
	roll = np.arctan2(R[2, 0], np.sqrt(np.power(R[2, 1],2) + np.power(R[2, 2], 2)))
	pitch = np.arctan2(R[2, 1], R[2, 2])

	print('Rotation along x (pitch): {:6.3f} degrees'.format(pitch * 180 / np.pi))
	print('Rotation along y (roll): {:6.3f} degrees'.format(roll * 180 / np.pi))
	print('Rotation along z (yaw): {:6.3f} degrees'.format(yaw * 180 / np.pi))
	
	if i < 27:
		print('\nClose plot to move onto next image\n')

	# Showcasing processed image with markers labeled along with 3D plot
	img = cv2.circle(img, X, 1, (255, 255, 255), 3)
	img = cv2.circle(img, Y, 1, (150, 150, 150), 3)
	img = cv2.circle(img, Z, 1, (60, 60, 60), 3)
	img = cv2.circle(img, A, 1, (127, 127, 127), 3)

	cv2.imshow('image', img)
	plot.showCamera(R, C)