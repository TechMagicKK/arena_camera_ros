import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class Redrawer:
    def __init__(self, img):
        self.img = img

        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.img)
        self.fig.subplots_adjust(bottom=0.4)
        slider_min = self.fig.add_axes([0.20, 0.1, 0.60, 0.03])
        slider_max = self.fig.add_axes([0.20, 0.15, 0.60, 0.03])
        self.slider_min = Slider(
                ax = slider_min,
                label="min",
                valmin=img.min(),
                valmax=img.max(),
                valinit=img.min(),
                orientation="horizontal",
            )
        self.slider_max = Slider(
                ax = slider_max,
                label="max",
                valmin=img.min(),
                valmax=img.max(),
                valinit=img.max(),
                orientation="horizontal",
            )

    def level(self, img, low, high):
        img = (img - low)/ (high - low) * 255#(high-low) + low
        return img

    def update(self, val):
        self.vmin = self.slider_min.val
        self.vmax = self.slider_max.val
        print(self.vmin, self.vmax)

        self.im.set_data(self.level(self.img, self.vmin, self.vmax))
        self.fig.canvas.draw_idle()

    def adjust_ir(self):
        self.slider_min.on_changed(self.update)
        self.slider_max.on_changed(self.update)
        plt.show()
