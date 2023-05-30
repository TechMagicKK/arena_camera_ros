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
from matplotlib.widgets import Button
import cv2

import paramiko
from scp import SCPClient


app = typer.Typer()


class ClickImage:
    def __init__(self, img):
        self.img = img
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.img)
        self.fig.canvas.mpl_connect("button_press_event", self.onclick)
        self.fig.canvas.mpl_connect("key_press_event", self.onkey)
        self.click_ok = False
        self.points = []

    def onkey(self, event):
        if event.key == "q":
            plt.close()
        elif event.key == "a":
            self.click_ok = True

    def onclick(self, event):
        if self.click_ok:
            print(f"{len(self.points)} x: {event.xdata}, y: {event.ydata})")
            self.points.append((event.xdata, event.ydata))
            self.click_ok = False

    def save(self):
        with open("/app/user_points.csv", "w") as f:
            for point in self.points:
                f.write(f"{round(point[0])},{round(point[1])}\n")


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


def send_data():
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("172.16.0.2", username="mnrobot2", key_filename="/root/tm_key")
        scp = SCPClient(client.get_transport())
        scp.put("/app/user_points.csv", remote_path="/home/mnrobot2/Work/mnrobot_core/mnrobot_arm/mnrobot_calibration/config")
        scp.put("/app/cam2board_mat.npy", remote_path="/home/mnrobot2/Work/mnrobot_core/mnrobot_arm/mnrobot_calibration/config")
        scp.close()
        print("Sent data success.")
    except:
        print("Can not sent data calibrated result to MiniPC.")


def calibrate(img_ir, img_depth):
    leveling = Redrawer(img_ir)
    leveling.adjust_ir()
    img_ir = leveling.get_adjusted_img()

    calib = CameraBoard(img_ir, img_depth)
    calib.calibrate()

    cl = ClickImage(img_ir)
    plt.show()
    cl.save()
    send_data()

@app.command()
def load():
    img_depth, img_ir = load_images()
    img_depth = np.array(img_depth, dtype=np.float32)

    img_ir = cv2.cvtColor(img_ir, cv2.COLOR_BGR2GRAY)
    calibrate(img_ir, img_depth)


@app.command()
def capture():
    camera = HeliosCamera()
    print("connecting to device")
    camera.connect_device()
    print("setting up streaming")
    camera.make_stream()
    print("make parameters")

    img_depth, img_ir = get_images(camera)
    fig, axs = plt.subplots(1, 2)
    im0 = axs[0].imshow(img_depth)
    im1 = axs[1].imshow(img_ir)
    axs[0].set_title("depth")
    axs[1].set_title("ir")

    def recapture(event):
        img_depth, img_ir = get_images(camera)
        im0.set_data(img_depth)
        im1.set_data(img_ir)
    def save_images(event):
        print("saving images")
        save_png(img_depth, "depth.png")
        save_png(img_ir, "ir.png")

    axrecapture = plt.axes([0.81, 0.05, 0.1, 0.075])
    axsave = plt.axes([0.7, 0.05, 0.1, 0.075])
    brecapture = Button(axrecapture, "Recapture")
    brecapture.on_clicked(recapture)

    bsave = Button(axsave, "Save images")
    bsave.on_clicked(save_images)
    plt.show()

    img_depth = np.array(img_depth, dtype=np.float32)
    #img_ir = cv2.cvtColor(img_ir, cv2.COLOR_BGR2GRAY)
    calibrate(img_ir, img_depth)


if __name__ == "__main__":
    app()
