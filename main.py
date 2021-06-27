# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:10:56 2021

@author: nicolas
"""

from bitstring import BitArray

from nexysio import nexysio
from genBitvector import genBitvector

#import os

def configVB(pos: int, dacs: list):
    
    vdacbits=BitArray()
    vdac = 0
    for vdac in dacs:
        if vdac > 1.8:
            print("\u001b[31mDAC on VB pos{} {}V exceeds 1.8V\n-> Set to 0V \u001b[0m".format(pos, vdac))
            vdac = 0

        dacvalue=int(vdac*16383/3.3)
        
        vdacbits.append(BitArray(uint=dacvalue, length=14))
        vdacbits.append(BitArray(uint=0, length=2))

    vdacbits.append(BitArray(uint=(1 << pos), length=8))

    return vdacbits


nexys = genBitvector()

nexys.openDevice(0)

# Test Write and read
nexys.writeRegister(0x09, 0x55)
nexys.readRegister(0x09)

# Bitvector len=20
testdata = BitArray(bin='01100010011010100011')

# Write to Asic
asicbits = nexys.writeSRasic(testdata, True)
#nexys.write(asicbits)

nexys.asicbitvector()

# Voltageboard
vdacbits = nexys.configVB(4, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])

vbbits = nexys.writeSRgecco(12, vdacbits, 8)
#nexys.write(vbbits)

nexys.close()
