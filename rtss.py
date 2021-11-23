#
# RTSS OSD text
#
import mmap


class RTSS:
    def __init__(self):
        self.shm = mmap.mmap(0, 102400, "RTSSSharedMemoryV2")

    def __del__(self):
        self.shm.close()

    def print_osd(self, text):
        shm = self.shm
        # clear osd text
        shm.seek(24 * 4, 0)
        shm.write(b'\0' * 256)
        shm.seek(24 * 4, 0)
        shm.write(text)
