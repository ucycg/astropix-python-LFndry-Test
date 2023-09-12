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
    asic.load_conf_from_yaml(2, "testconfig")
    asic.update_asic()

    vboard1 = Voltageboard(handle, 4, (8, [0, 0, 1.1, 1, 0, 0, 0.7, 1.1]))
    vboard1.vcal = 0.989
    vboard1.vsupply = 2.82
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

    scan_method = 'threshold'
    noise_run = False
    v_start = 0.0
    v_stop = 0.6
    vinj = 0.3
    vth = 1.2
    counts = 1
    row = 10
    col = None
    inj_pulses = 100

    timestr = time.strftime("dig_inj_scan_%Y%m%d-%H%M%S")
    with open("log/%s.log" % timestr, "w", buffering=1, newline='\n') as file:
        file.write(f"Voltageboard settings: {vboard1.dacvalues}\n")
        file.write(f"Digital: {asic.asic_config['digitalconfig']}\n")
        file.write(f"Biasblock: {asic.asic_config['biasconfig']}\n")
        file.write(f"IDAC: {asic.asic_config['idacs']}\n")
        file.write(f"VDAC: {asic.asic_config.get('vdacs')}\n")
        file.write(f"Receiver: {asic.asic_config['recconfig']}\n")
        file.write(f"Noise run: {noise_run}\n")
        file.write(f"Scan_method: {scan_method}\n")
        file.write(f"Inj pulses: {inj_pulses}\n")

        Scan.scan_binsearch(asic, vboard1, inj, nexys, file,
                            vinj=vinj,
                            vth=vth,
                            v_start=v_start,
                            v_stop=v_stop,
                            scan_method=scan_method,
                            row=row,
                            col=col,
                            counts=counts,
                            inj_pulses=inj_pulses,
                            v_vdd33=vboard1.vsupply)

    # Close connection
    nexys.close()


if __name__ == "__main__":
    main()
