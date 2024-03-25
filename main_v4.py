# -*- coding: utf-8 -*-
""""""
"""
Created on Sat Jun 26 00:10:56 2021

@author: Nicolas Striebig
"""
from modules.asic import Asic
from modules.injectionboard import Injectionboard
from modules.nexysio import Nexysio
from modules.voltageboard import Voltageboard
from modules.decode import Decode
from utils.utils import wait_progress


def main():

    nexys = Nexysio()

    # Open FTDI Device with Index 0
    # handle = nexys.open(0)
    handle = nexys.autoopen()

    # Write and read directly to register
    # Example: Write 0x55 to register 0x09 and read it back
    nexys.write_register(0x09, 0x55, True)
    nexys.read_register(0x09)

    #
    # Configure ASIC
    #

    # Write to asicSR
    asic = Asic(handle)
    asic.load_conf_from_yaml(4, "testconfig_v4")

    # Enable Pixel (4,0)
    asic.enable_ampout_col(4)
    asic.enable_inj_col(4)
    asic.enable_inj_row(0)
    asic.enable_pixel(4, 1)

    asic.write_conf_to_yaml("testconfig_v4_write")
    asic.update_asic()

    # Currently enables all hitbuffers and sets tdac values to 0
    asic.update_asic_tdacrow(0)

    #
    # Configure Voltageboard
    #

    # Configure 8 DAC Voltageboard in Slot 4 with list values
    # 3 = Vcasc2, 4=BL, 7=Vminuspix, 8=Thpix
    vboard1 = Voltageboard(handle, 4, (8, [1.8, 0, 1.1, 1, 0, 0, 0.8, 1.15]))

    # Set measured 1V for one-point calibration
    vboard1.vcal = 0.989
    vboard1.vsupply = 3.3

    # Update voltageboards
    vboard1.update_vb()

    #
    # Configure Injectionboard
    #

    inj = Injectionboard(handle, 3, onchip=False)

    # Set Injection Params for 330MHz patgen clock
    inj.period = 10
    inj.clkdiv = 10
    inj.initdelay = 100
    inj.cycle = 0
    inj.pulsesperset = 1
    inj.vcal = vboard1.vcal
    inj.vsupply = vboard1.vsupply
    inj.amplitude = 0.3

    #
    # SPI
    #

    # Enable SPI
    nexys.spi_enable()
    nexys.spi_reset()

    # Set SPI clockdivider
    # freq = 100 MHz/spi_clkdiv
    nexys.spi_clkdiv = 40

    # Send Routing command
    nexys.send_routing_cmd()

    # Reset SPI Read FIFO
    nexys.spi_reset()

    inj.start()

    wait_progress(3)
    while True:
        # Read max. 100 times or until read FIFO is empty
        readout = nexys.read_spi(100)

        decode = Decode(bytesperhit=8)
        list_hits = decode.hits_from_readoutstream(readout)

        print(decode.decode_astropix4_hits(list_hits).to_string())


if __name__ == "__main__":
    main()
