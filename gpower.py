#
# A simple python PC power monitor
#
import time
from axipsu import AXIPSU
from nvsmi import NVGPU
from intelcpu import INTELCPU
from rtss import RTSS

sample_time = 2
period = 0
energy = 0

psu = AXIPSU()
gpu = NVGPU()
cpu = INTELCPU()
rtss = RTSS()

while 1:
    time.sleep(sample_time)

    p = psu.get_power()
    energy += p * sample_time
    period += sample_time
    avg_power = energy / period
    gp = gpu.get_power()
    cp = cpu.get_power()
    op = p - cp - gp
    text = 'PWR cur {:>5.1f} avg {:>5.1f} GPU {:>5.1f} Others {:>5.1f} CPU {:.1f}'.format(p, avg_power, gp, op, cp) 
    print(text, end='\r', flush=True)
    rtss.print_osd(bytes(text + '\n', 'ascii'))
