# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:10:56 2021

@author: Nicolas Striebig
"""
from bitstring import BitArray

from modules.gecco import Gecco
from modules.injection import Injection


def main():
    nexys = Gecco()

    # Open FTDI Device with Index 0
    nexys.open_device(0)

    # Write 0x55 to register 0x09 and read it back
    nexys.write_register(0x09, 0x55, True)
    nexys.read_register(0x09)

    # Generate pattern for asicSR
    asicconfig = nexys.asic_vector()

    #
    # Write Asicconfig
    #

    # Write zeros
    dummyconfig = BitArray(uint=0, length=245)
    dummybits = nexys.write_sr_asic(dummyconfig, True)

    # Write config
    asicbits = nexys.write_sr_asic(asicconfig, True)
    nexys.write(dummybits+asicbits)

    #
    # Configure Voltageboard
    #

    # Set measured 1V for one-point calibration
    nexys.vcal = 0.988

    # Configure Voltageboard in Slot 4 with list values
    vdacbits = nexys.vb_vector(4, [0.1, 0.2, 0.3, 1, 0.5, 0.6, 0.7, 0.8])

    # Generate pattern for Voltageboard Register 12 with clockdivider 8
    vbbits = nexys.write_sr_gecco(12, vdacbits, 8)
    nexys.write(vbbits)

    #
    # Injection
    #

    # Set Injection level
    injdacbits = nexys.write_sr_gecco(12, nexys.vb_vector(5, [1, 1]), 8)
    nexys.write(injdacbits)

    inj = Injection()

    # Set Injection Params
    inj.period = 100
    inj.clkdiv = 300
    inj.initdelay = 100
    inj.cycle = 0
    inj.pulsesperset = 1

    # Stop injection
    stopinj = inj.stop()
    nexys.write(stopinj)

    # Configure injection
    injvector = inj.configureinjection()
    nexys.write(injvector)

    # Start Injection
    startinj = inj.start()
    nexys.write(startinj)

    # Close connection
    nexys.close()


if __name__ == "__main__":

    main()
