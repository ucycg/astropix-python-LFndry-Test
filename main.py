# -*- coding: utf-8 -*-
""""""
"""
Created on Sat Jun 26 00:10:56 2021

@author: Nicolas Striebig (Original Author), Justin Cott (Contributor)
"""
import binascii

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

    # First Select Bottom Chip of Lfoundry astropix Double Testchip for config. 
    nexys.write_register(0x34, 0x00, True)  # flip demux to Top Chip
    nexys.read_register(0x34)

    #
    # Configure ASIC
    #

    # Write to asicSR
    asic = Asic(handle)
    asic.load_conf_from_yaml(1, "testconfig_lf_tst")
    
    # asic.asic_config['idacs']['vncomp'] = 60
    # asic.write_conf_to_yaml("testconfig_v3_write")  NO LETS NOT OVERWRITE JUSTIN
    # asic.load_conf_from_yaml(2,"testconfig_write")
    #asic.enable_ampout_col(5)
    #asic.enable_inj_col(5)
            #TALK WITH NICOLAS!!! WHAT NEEDS TO HAPPEN HERE!
    #asic.enable_inj_row(0)
    #asic.enable_pixel(0, 1)
    #asic.enable_pixel(0, 2)
    #asic.enable_pixel(0, 3)
    asic.update_asic()

    #Second HOPEFULLY SWITCH TO TOP CHIP WITH INTERNAL FPGA DEMUX

    nexys.read_register(0x34)
    #nexys.write_register(0x34, 0x01, True)  # flip demux to Top Chip
    #nexys.read_register(0x34)
    #asic.update_asic()

    # now its necessary to switch the hardware connection of the FPGA

    #asic.readback_asic() # JUSTIN TRYS TO UNDESTAND CODE --> GETS ME TOO MUCH OUTPUT

    # Example: Update Config Bit
    # asic.digitalconfig['En_Inj17'] = 1
    # asic.dacs['vn1'] = 63
    # asic.update_asic()

    #
    # Configure Voltageboard
    #

    # Configure 8 DAC Voltageboard in Slot 4 with list values
    # 5 = Vcasc, 6=VPBias, 7=VTh, 8=BL
    #vboard1 = Voltageboard(handle, 4, (8, [0, 0, 0, 0, 1.1, 1.2, 1.1, 1.0]))
    vboard1 = Voltageboard(handle, 4, (8, [0, 0, 0, 0, 0, 0, 0, 0]))

    # Set measured 1V for one-point calibration
    vboard1.vcal = 0.989
    vboard1.vsupply = 2.77

    # Update voltageboards
    vboard1.update_vb()

    # Write only first 3 DACs, other DACs will be 0
    # vboard1.dacvalues = (8, [1.2, 1, 1])
    # vboard1.update_vb()

    #
    # Configure Injectionboard
    #

    inj = Injectionboard(handle, 3)

    # Set Injection Params for 330MHz patgen clock
    inj.period = 100                        # Time Unit in ms
    inj.clkdiv = 400   
    inj.initdelay = 10000                   
    inj.cycle = 0
    inj.pulsesperset = 1                    # i.e. set this to 1 gives 2 pulses total
    inj.vcal = vboard1.vcal
    inj.vsupply = vboard1.vsupply
    inj.amplitude = 0.4                      #Unit Volt!

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
    # asic_bitvector = asic.gen_asic_vector()
    # spi_data = nexys.asic_spi_vector(asic_bitvector, True, 10)

    # Write Config via spi
    # nexys.write_spi(spi_data, False, 8191)

    # Send Routing command
    nexys.send_routing_cmd()

    # Reset SPI Read FIFO
    nexys.spi_reset()

    inj.start()

    wait_progress(3)

    # Read max. 10 times or until read FIFO is empty
    readout = nexys.read_spi_fifo(10)

    print(binascii.hexlify(readout))

    decode = Decode()
    list_hits = decode.hits_from_readoutstream(readout)

    print(decode.decode_astropix2_hits(list_hits))

    #inj.stop()

    # Close connection
    
    nexys.close()


if __name__ == "__main__":
    main()
