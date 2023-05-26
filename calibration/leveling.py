import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider

class Redrawer:
    def __init__(self, img):
        self.img = img

        self.fig, self.ax = plt.subplots()
        # self.ax.imshow(self.level(img, min(img), max(img)) )
        self.im = self.ax.imshow(img)
        self.fig.subplots_adjust(bottom=0.4)
        # Create the RangeSlider
        slider_ax = self.fig.add_axes([0.20, 0.1, 0.60, 0.03])
        self.slider = RangeSlider(slider_ax, "Threshold", img.min(), img.max())

    def level(self, img, low, high):
        img = img - low/ (high - low) * (high-low) + low
        return img

    def update(self, val):
        self.vmin = val[0]
        self.vmax = val[1]
        self.im.norm.vmin = self.vmin
        self.im.norm.vmax = self.vmax

        self.fig.canvas.draw_idle()

    def adjust_ir(self):
        self.slider.on_changed(self.update)
        plt.show()
