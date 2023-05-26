import numpy as np
from arena_api.system import system
from tenacity import retry, wait_fixed, stop_after_attempt
import ctypes
import copy


class HeliosCamera:
    def __init__(self):
        self.device = None

    def __del__(self):
        if self.device is not None:
            system.destroy_device()

    @retry(stop=stop_after_attempt(1), wait=wait_fixed(10))
    def connect_device(self):
        if self.device is None:
            devices = system.create_device()
            if not devices:
                raise Exception("No device found! Please connect a device")
            else:
                print(f'Created {len(devices)} device(s)')
                self.device = devices[0]

    def make_stream(self):
        stream_node = self.device.tl_stream_nodemap
        stream_node["StreamAutoNegotiatePacketSize"].value = True
        stream_node["StreamPacketResendEnable"].value = True

    def setup(self, pixelformat="Coord3D_C16"):

        nodes = self.device.nodemap.get_node(["Width", "Height", "PixelFormat", "Scan3dHDRMode"])
        nodes["Scan3dHDRMode"].value = "StandardHDR"
        nodes["PixelFormat"].value = pixelformat

    def get_image(self):
        image_buffer = self.device.get_buffer()
        pdata_as16 = ctypes.cast(image_buffer.pdata, ctypes.POINTER(ctypes.c_ushort))
        nparray_reshaped = np.ctypeslib.as_array(pdata_as16, (image_buffer.height, image_buffer.width))
        ret = copy.deepcopy(nparray_reshaped)
        self.device.requeue_buffer(image_buffer)
        return ret
