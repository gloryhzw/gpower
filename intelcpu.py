#
# Read Intel CPU power by Intel power gadget API
#
# https://www.intel.com/content/www/us/en/developer/articles/training/using-the-intel-power-gadget-30-api-on-windows.html
# https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html
#
from ctypes import *


class INTELCPU:
    def __init__(self):
        self.lib = CDLL('./EnergyLib64.dll')
        r = self.lib.IntelEnergyLibInitialize()
        self.lib.ReadSample()

    # def __del__(self):

    def get_power(self):
        self.lib.ReadSample()
        nmsr = c_int()
        self.lib.GetNumMsrs(byref(nmsr))
        # print(nmsr.value)

        name = create_unicode_buffer(128)

        for i in range(0, nmsr.value):
            funcID = c_int()
            self.lib.GetMsrFunc(i, byref(funcID))
            if funcID.value == 1:
                self.lib.GetMsrFunc(i, byref(funcID))
                self.lib.GetMsrName(i, name)

                #print(i, len(name.value), name.value)
                if name.value == 'Processor':
                    double = (c_double * 3)()
                    n = c_int()
                    self.lib.GetPowerData(0, i, byref(double), byref(n))
                    return double[0]
                    # for j in range(0, n.value):
                    #    print(j, double[j])

        return 0

#cpu = INTELCPU()
#import time
# time.sleep(1)
# print(cpu.get_power())
