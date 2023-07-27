import numpy as np
import cv2 as cv
import math


class CameraBoard():

    CHECKERBOARD = (6, 7)

    CAM_INTRINSIC = np.array(
        [[524.046, 0.0, 323.377],
        [0.0, 524.046, 237.054],
        [0.0, 0.0, 1.0]])

    def __init__(self, mono: np.array, depth: np.array) -> None:
        self._mono_data = np.uint8(mono)
        self._depth_data = depth

    def calibrate(self) -> None:
        """
        Find the chess board corners
        If desired number of corners are found in the image then ret = true
        """
        ret, corners = cv.findChessboardCorners(
            self._mono_data, CameraBoard.CHECKERBOARD, cv.CALIB_CB_ADAPTIVE_THRESH +
            cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)

        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display
        them on the images of checker board
        """
        if ret:
            # refining pixel coordinates for given 2d points.
            corners2 = cv.cornerSubPix(self._mono_data, corners, (5, 5), (-1, -1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            debug_data = self._mono_data.copy()
            debug_data = cv.cvtColor(debug_data, cv.COLOR_GRAY2RGBA)
            cv.drawChessboardCorners(debug_data, (7,7), corners2, True)
            for i, c in enumerate(corners2):
                cv.putText(debug_data,
                        text=str(i),
                        org=(c[0][0], c[0][1]),
                        fontFace=cv.FONT_HERSHEY_SIMPLEX,
                        fontScale=.5,
                        color=(0, 255, 0),
                        thickness=1,
                        lineType=cv.LINE_4)

            uv_point1 = corners2[41][0]
            uv_point2 = corners2[36][0]
            print(f"point 1: {uv_point1}")
            print(f"point 2: {uv_point2}")

            fx = CameraBoard.CAM_INTRINSIC[0][0]
            fy = CameraBoard.CAM_INTRINSIC[1][1]
            cx = CameraBoard.CAM_INTRINSIC[0][2]
            cy = CameraBoard.CAM_INTRINSIC[1][2]

            # calculate x, y of translation matrix.
            # tz = self._depth_data[int(uv_point1[1]), int(uv_point1[0])] * 0.001
            tz = np.mean(self._depth_data[int(uv_point1[1])-5:int(uv_point1[1])+5, int(uv_point1[0])-5:int(uv_point1[0])+5]) * 0.001
            tx = (uv_point1[0] - cx) / fx * tz
            ty = (uv_point1[1] - cy) / fy * tz

            # calculate rotation matrix by using two points in UV space.
            theta = math.atan2((uv_point2[1] - uv_point1[1]), (uv_point2[0] - uv_point1[0]))
            print(f"theta angle: {theta}")
            print(f"tx: {tx}")
            print(f"tz: {tz}")
            cam2board_mat = np.zeros((4, 4))
            cam2board_mat[0][0] = math.cos(theta)
            cam2board_mat[0][1] = -math.sin(theta)
            cam2board_mat[1][0] = math.sin(theta)
            cam2board_mat[1][1] = math.cos(theta)
            cam2board_mat[2][2] = 1
            cam2board_mat[0][3] = tx
            cam2board_mat[1][3] = ty
            cam2board_mat[2][3] = tz
            cam2board_mat[3][3] = 1
            print(f"camera to board matrix: \n{cam2board_mat}\n")
            np.save("/app/cam2board_mat.npy", cam2board_mat)
            return debug_data

        else:
            print("Can not find any corner !!!")
