# -*- coding: utf-8 -*-
""""""
"""
Created on Sat Jun 26 00:10:56 2021

@author: Nicolas Striebig
"""

import time

from modules.asic import Asic
from modules.injectionboard import Injectionboard
from modules.nexysio import Nexysio
from modules.voltageboard import Voltageboard
from modules.scan import Scan


def main():

    nexys = Nexysio()
    handle = nexys.autoopen()

    asic = Asic(handle)
    asic.load_conf_from_yaml(3, "testconfig_v3")
    asic.update_asic()

    vboard1 = Voltageboard(handle, 4, (8, [0, 0, 1.1, 1, 0, 0, 0.7, 1.1]))
    vboard1.vcal = 0.989
    vboard1.vsupply = 3.3
    vboard1.update_vb()

    inj = Injectionboard(handle, 3)
    inj.period = 100
    inj.clkdiv = 100
    inj.initdelay = 100
    inj.cycle = 1
    inj.pulsesperset = 100
    inj.vcal = vboard1.vcal
    inj.vsupply = vboard1.vsupply
    inj.amplitude = 0.3

    nexys.spi_enable()
    nexys.spi_reset_fpga_readout()
    nexys.spi_clkdiv = 40
    nexys.send_routing_cmd()
    nexys.spi_reset_fpga_readout()

    noise_run = False
    steps = 5
    counts = 10
    vth_start = 1.15

    timestr = time.strftime("dig_inj_scan_%Y%m%d-%H%M%S")
    file = open("log/%s.log" % timestr, "w", buffering=1, newline='\n')
    file.write(f"Voltageboard settings: {vboard1.dacvalues}\n")

    file.write(f"Digital: {asic.asic_config['digitalconfig']}\n")
    file.write(f"Biasblock: {asic.asic_config['biasconfig']}\n")
    file.write(f"DAC: {asic.asic_config['idacs']}\n")
    file.write(f"Receiver: {asic.asic_config['recconfig']}\n")
    file.write(f"Noise run: {noise_run}\n")
    file.write(f"vth_start: {vth_start}\n")
    file.write(f"Steps: {steps}\n")
    file.write(f"Runs per Step: {counts}\n")

    # Scan.inj_scan(asic, vboard1, inj, nexys, file,
    #               vth=1.15, stepsize=0.02, step=20, vinj_start=0.0, col=10, row=10, counts=1)
    Scan.inj_scan_binsearch(asic, vboard1, inj, nexys, file,
                            vth=1.15, steps=20, vinj_start=0.0, row=10, counts=1)

    # Close connection
    nexys.close()


if __name__ == "__main__":
    main()
