# 1. get gazou
# 2. adjust gazou
# 3. corner detection
# 4. touch up
#
import typer
from helios_camera import HeliosCamera
from leveling import Redrawer

import matplotlib.pyplot as plt
import cv2

app = typer.Typer()


def get_images(camera):
    camera.setup()
    print("start fetching image")
    with camera.device.start_stream(1):
        img_depth = camera.get_image()
    camera.setup("Mono16")
    with camera.device.start_stream(1):
        img_ir = camera.get_image()
    return img_depth, img_ir

def save_png(img, png_name):
    cv2.imwrite(png_name, img)

def load_images():
    img_depth = cv2.imread("depth.png")
    img_ir = cv2.imread("ir.png")
    return img_depth, img_ir

@app.command()
def local():
    img_depth, img_ir = load_images()
    leveling = Redrawer(img_ir)
    leveling.adjust_ir()
    img_ir = leveling.level(img_ir, leveling.vmin, leveling.vmax)
    plt.imshow(img_ir)
    plt.show()


@app.command()
def main():
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

        save_png(img_depth, "depth.png")
        save_png(img_ir, "ir.png")

        print("ok (enter) recapture (r)")
        input()
        if input() == "r":
            retry = True
        else:
            retry = False


if __name__ == "__main__":
    app()
