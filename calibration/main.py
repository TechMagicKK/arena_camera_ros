# 1. get gazou
# 2. adjust gazou
# 3. corner detection
# 4. touch up
#
import typer
from helios_camera import HeliosCamera
from leveling import Redrawer
from calibrate import CameraBoard
import numpy as np

import matplotlib.pyplot as plt
import cv2

app = typer.Typer()


class ClickImage:
    def __init__(self, img):
        self.img = img
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.img)
        self.fig.canvas.mpl_connect("button_press_event", self.onclick)

    def onclick(self, event):
        print(f"x: {event.xdata}, y: {event.ydata})")
        # print(self.img[int(event.ydata), int(event.xdata)])


def get_images(camera):
    camera.setup()
    print("start fetching image")
    with camera.device.start_stream(1):
        img_depth = camera.get_image()
    camera.setup("Mono16")
    with camera.device.start_stream(1):
        img_ir = camera.get_image()
    print(f"scale {camera.scale_z}")
    img_depth = np.array(img_depth, dtype=np.float32) * camera.scale_z
    return np.uint16(img_depth), img_ir


def save_png(img, png_name):
    cv2.imwrite(png_name, img)


def load_images():
    img_depth = cv2.imread("depth.png", cv2.IMREAD_ANYDEPTH)
    img_ir = cv2.imread("ir.png")
    return img_depth, img_ir


@app.command()
def load():
    img_depth, img_ir = load_images()
    img_depth = np.array(img_depth, dtype=np.float32)

    img_ir = cv2.cvtColor(img_ir, cv2.COLOR_BGR2GRAY)
    leveling = Redrawer(img_ir)
    leveling.adjust_ir()
    img_ir = leveling.get_adjusted_img()

    calib = CameraBoard(img_ir, img_depth)
    calib.calibrate()

    cl = ClickImage(img_ir)
    plt.show()


@app.command()
def capture():
    camera = HeliosCamera()
    print("connecting to device")
    camera.connect_device()
    print("setting up streaming")
    camera.make_stream()
    print("make parameters")

    retry = True
    while retry:
        img_depth, img_ir = get_images(camera)
        plt.subplot(1, 2, 1)
        plt.imshow(img_depth)
        plt.subplot(1, 2, 2)
        plt.imshow(img_ir)
        plt.show()

        print("ok (enter) recapture (r)")
        if input() == "r":
            retry = True
        else:
            retry = False

    print("saving images")
    save_png(img_depth, "depth.png")
    save_png(img_ir, "ir.png")

    img_depth = np.array(img_depth, dtype=np.float32)
    img_ir = cv2.cvtColor(img_ir, cv2.COLOR_BGR2GRAY)
    leveling = Redrawer(img_ir)
    leveling.adjust_ir()
    img_ir = leveling.get_adjusted_img()

    print("calibrating camera")
    calib = CameraBoard(img_ir, img_depth)
    calib.calibrate()

    cl = ClickImage(img_ir)
    plt.show()


if __name__ == "__main__":
    app()
