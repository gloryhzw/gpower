#
# A simple NVIDIA GPU power reader by NVML API
#
# https://docs.nvidia.com/deploy/nvml-api/index.html
# https://pypi.org/project/nvidia-ml-py/
#
from ctypes import *


class NVGPU:
    def __init__(self):
        self.nvmlLib = CDLL('C:/Windows/System32/nvml.dll')
        r = self.nvmlLib.nvmlInit_v2()
        self.handle = c_void_p()
        self.nvmlLib.nvmlDeviceGetHandleByIndex_v2(0, byref(self.handle))

    def __del__(self):
        self.nvmlLib.nvmlShutdown()

    def get_power(self):
        power = c_int()
        self.nvmlLib.nvmlDeviceGetPowerUsage(self.handle, byref(power))
        return power.value / 1000

#gpu = NVGPU()
# print(gpu.get_power())
