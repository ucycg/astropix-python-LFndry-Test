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
    # asic.update_asic()

    # Update single parameter
    # asic.digitalconfig[f'En_Inj17'] = 1
    # asic.update_asic()

    #
    # Configure Voltageboard
    #

    # Configure 8 DAC Voltageboard in Slot 4 with list values
    vboard1 = Voltageboard(handle, 4, (8, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]))

    # Set measured 1V for one-point calibration
    vboard1.vcal = 0.989

    # Update voltageboards
    # vboard1.update_vb()

    # Write only first 3 DACs, other DACs will be 0
    # vboard1.dacvalues = (8, [1.2, 1, 1])
    # vboard1.update_vb()

    #
    # Configure Injectionboard
    #

    # Set Injection level
    injvoltage = Voltageboard(handle, 5, (2, [0.5, 0.0]))
    injvoltage.vcal = 0.989
    injvoltage.update_vb()

    inj = Injectionboard(handle)

    # Set Injection Params for 330MHz patgen clock
    inj.period = 100
    inj.clkdiv = 300
    inj.initdelay = 100
    inj.cycle = 0
    inj.pulsesperset = 1

    # Start injection
    inj.start()

    #
    # SPI
    #

    # Enable SPI
    nexys.spi_enable()
    nexys.spi_reset()

    # Set SPI clockdivider
    # freq = 100 MHz/spi_clkdiv
    nexys.spi_clkdiv = 255

    # Generate bitvector for SPI ASIC config
    asic_bitvector = asic.gen_asic_vector()
    print(f'Asic Bitvector: {asic_bitvector}\n')

    spi_data = nexys.asic_spi_vector(asic_bitvector, 1)
    print(f'Asic SPIdata: {spi_data}\n')

    # Write bitvector via spi
    # nexys.write_spi(spi_data, 4095)

    # Reset SPI (Clear FIFOs)
    nexys.spi_reset()

    # Write to MOSI (should be multiple of 4 Bytes)

    # Read enable command
    nexys.write_spi(bytearray(b'\x50\x00\x00\x00'))

    # clock in another e.g. 16 bytes from MISO by writing 2x 8bytes
    i = 0
    while i < 2:
        nexys.write_spi(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'))
        i += 1

    # Read if ReadFIFO (Width 8 Bytes) is not empty
    while not (int.from_bytes(nexys.read_register(21), 'big') & 16):
        print(f'Read SPI: {nexys.read_spi(8)}')

    nexys.spi_reset()

    # Close connection
    nexys.close()


if __name__ == "__main__":
    main()
