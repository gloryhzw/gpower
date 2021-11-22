#
# Corsair AX1500i power monitor python
#
# Reference: https://github.com/ka87/cpsumon
#
import time
from nvsmi import NVGPU
from intelcpu import INTELCPU
from ctypes import *


class AXIPSU:
    debug = 0

    enc = [0x55, 0x56, 0x59, 0x5a, 0x65, 0x66, 0x69, 0x6a,
           0x95, 0x96, 0x99, 0x9a, 0xa5, 0xa6, 0xa9, 0xaa]

    dec = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
           0x20, 0x21, 0x00, 0x12, 0x22, 0x23, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x14, 0x24,
           0x25, 0x00, 0x16, 0x26, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x28, 0x29, 0x00, 0x1a,
           0x2a, 0x2b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1c, 0x2c, 0x2d, 0x00, 0x1e, 0x2e,
           0x2f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
           0x00]

    def send(self, h, b, size, encode=True):
        enc = self.enc
        if encode:
            nsize = size * 2 + 2
            nb = create_string_buffer(nsize)
            command = 0
            nb[0] = enc[(command << 1) & 0xf] & 0xfc
            nb[nsize - 1] = 0

            if self.debug >= 2:
                for i in range(0, size):
                    print(i, hex(int.from_bytes(b[i], byteorder='little')))

            j = 1
            for i in range(1, size + 1):
                bm1 = int.from_bytes(b[i - 1], byteorder='little')
                nb[j] = enc[bm1 & 0xf]
                j += 1
                nb[j] = enc[bm1 >> 4]
                j += 1

            if self.debug >= 2:
                for i in range(0, nsize):
                    print(i, hex(int.from_bytes(nb[i], byteorder='little')))

            size = nsize
            b = nb

        n = c_int()
        r = self.m.SI_Write(h, b, size, byref(n), 0)
        if self.debug:
            print("W", r, b, n.value)

    def recv(self, h, size, decode=True):
        dec = self.dec
        rb = create_string_buffer(size)

        n = c_int()
        r = self.m.SI_Read(h, rb, size, byref(n), 0)
        if self.debug:
            print("R", r, rb[0], n.value)

        size = n.value

        if decode:
            nsize = int(size / 2)
            nb = create_string_buffer(nsize)

            b = int.from_bytes(rb[0], byteorder='little')

            if ((dec[b] & 0xf) >> 1) != 7:
                print("read wrong reply")

            j = 0
            for i in range(1, size + 1, 2):
                b = int.from_bytes(rb[i], byteorder='little')
                b1 = int.from_bytes(rb[i + 1], byteorder='little')
                nb[j] = (dec[b] & 0xf) | ((dec[b1] & 0xf) << 4)
                j += 1

            ret = nb
        else:
            ret = rb

        return ret

    def read_data_psu(self, h, reg, len):
        d1 = bytes([19, 3, 6, 1, 7, len, reg])
        d2 = bytes([8, 7, len])

        self.send(h, create_string_buffer(d1), 7)
        r = self.recv(h, 512)

        self.send(h, create_string_buffer(d2), 3)
        r = self.recv(h, 512)

        return r

    def b2f(self, data):
        b = [int.from_bytes(x, byteorder='little') for x in data]

        p1 = (b[1] >> 3) & 31
        if (p1 > 15):
            p1 -= 32

        p2 = (b[1] & 7) * 256 + b[0]
        if (p2 > 1024):
            p2 = -(65536 - (p2 | 63488))

        return p2 * pow(2.0, p1)

    def get_power(self):
        r = self.read_data_psu(self.h, 0xee, 2)
        return self.b2f(r)

    def __init__(self):
        m = CDLL('./SiUSBXp.dll')
        self.m = m

        n = c_int()
        d = m.SI_GetNumDevices(byref(n))

        s = create_string_buffer(64)

        if self.debug >= 2:
            for i in range(0, 5):
                d = m.SI_GetProductString(0, s, i)
                print(i, s.value.decode())

        t1 = c_int()
        t2 = c_int()
        r = m.SI_GetTimeouts(byref(t1), byref(t2))
        r = m.SI_GetDLLVersion(byref(t1), byref(t2))
        r = m.SI_GetDriverVersion(byref(t1), byref(t2))
        r = m.SI_SetTimeouts(1000, 1000)

        h = c_int()
        r = m.SI_Open(0, byref(h))
        self.h = h

        r = m.SI_SetBaudRate(h, 115200)
        r = m.SI_FlushBuffers(h, 1, 1)

        for i in range(0, 3):
            self.send(h, create_string_buffer(
                bytes([17, 2, 100, 0, 0, 0, 0])), 7)
            self.recv(h, 512)

    def __del__(self):
        self.m.SI_Close(self.h)
