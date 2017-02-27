# By Frank Yu

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

def showCamera(R, C):
	""" Plots to scale figure of camera and QR image position """
	fig = plt.figure()
	ax = fig.gca(projection='3d')

	# Drawing QR code
	X = np.arange(-0.044, 0.044, 0.001)
	Y = np.arange(-0.044, 0.044, 0.001)
	X, Y = np.meshgrid(X, Y)
	Z = 0
	QR = ax.plot_surface(X, Y, Z)

	# Drawing quiver to indicate the top of the pattern
	top = ax.quiver(0, 0, 0, 0, 1, 0, length=0.1, colors='k')

	# Drawing camera position
	X = C[0]
	Y = C[1]
	Z = C[2]

	camera = ax.plot(X, Y, Z, 'bo', label="Camera")

	# Drawing camera direction
	c_dir = np.dot(R, np.matrix([0, 0, 1]).transpose())
	intercept = C - np.multiply((C[2] / c_dir[2]), c_dir)

	X = [C.item(0), intercept.item(0)]
	Y = [C.item(1), intercept.item(1)]
	Z = [C.item(2), intercept.item(2)]

	c_dir = ax.plot(X, Y, Z, 'r-', label="Camera Direction")

	"""
	Drawing quiver to indicate the top of the iphone when held vertically.
	This helps clarify rotation in z axis for top down shots
	"""
	c_top = np.dot(R, np.matrix([0, 1, 0]).transpose())
	c_top = ax.quiver(C[0], C[1], C[2], c_top[0], c_top[1], c_top[2], 
														length=0.1, colors='k')

	# Formatting plot.
	ax.set_zlim(-0, 1)
	ax.set_xlim(-0.5, 0.5)
	ax.set_ylim(-0.5, 0.5)
	ax.set_xlabel('X (meters)')
	ax.set_ylabel('Y (meters)')
	ax.set_zlabel('Z (meters)')
	ax.legend(numpoints=1)

	plt.show()