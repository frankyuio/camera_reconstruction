# By Frank Yu

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

def show_camera(r_matrix, c_matrix):
    """ Plots to scale figure of camera and QR image position """
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Drawing QR code
    qr_x = np.arange(-0.044, 0.044, 0.001)
    qr_y = np.arange(-0.044, 0.044, 0.001)
    qr_x, qr_y = np.meshgrid(qr_x, qr_y)
    qr_z = 0
    qr_plot = ax.plot_surface(qr_x, qr_y, qr_z)

    # Drawing quiver to indicate the top of the pattern
    top = ax.quiver(0, 0, 0, 0, 1, 0, length=0.1, colors='k')

    # Drawing camera position
    camera_x = c_matrix[0]
    camera_y = c_matrix[1]
    camera_z = c_matrix[2]

    camera = ax.plot(camera_x, camera_y, camera_z, 'bo', label="Camera")

    # Drawing camera direction
    camera_dir = np.dot(r_matrix, np.matrix([0, 0, 1]).transpose())
    intercept = c_matrix - np.multiply((c_matrix[2] / camera_dir[2]), camera_dir)

    camera_dir_x = [c_matrix.item(0), intercept.item(0)]
    camera_dir_y = [c_matrix.item(1), intercept.item(1)]
    camera_dir_z = [c_matrix.item(2), intercept.item(2)]

    camera_plot = ax.plot(camera_dir_x, camera_dir_y, camera_dir_z, 'r-', label="Camera Direction")

    """
    Drawing quiver to indicate the top of the iphone when held vertically.
    This helps clarify rotation in z axis for top down shots
    """
    camera_top = np.dot(r_matrix, np.matrix([0, 1, 0]).transpose())
    camera_top = ax.quiver(c_matrix[0], c_matrix[1], c_matrix[2], camera_top[0], camera_top[1],
                           camera_top[2], length=0.1, colors='k')

    # Formatting plot.
    ax.set_zlim(-0, 1)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')
    ax.legend(numpoints=1)

    plt.show()
