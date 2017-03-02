# Camera Reconstruction
Reconstruct camera position and rotation from images of QR code. 
Dimensions of QR pattern and camera intrinsic parameters are known.

### Requirements
- python 2.7
- matplotlib
- numpy
- cv2

### To launch
```bash
cd repo/dir
py -2 .
```

## Approach
1. Process image and identify points on the image that can be mapped to points in real life.
2. Use image coordinates and real life coordinates to establish a relationship between camera and image
3. Plot the image and camera position.

## Demonstration
![alt text](https://github.com/QFrankY/camera_reconstruction/blob/master/demo.png "Camera Reconstruction Demo")
