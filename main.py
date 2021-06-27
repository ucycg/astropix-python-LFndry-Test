# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:10:56 2021

@author: Nicolas Striebig
"""

from modules.gecco import gecco
from bitstring import BitArray

nexys = gecco()

nexys.openDevice(0)

# Test Write and read
nexys.writeRegister(0x09, 0x55)
nexys.readRegister(0x09)

# Bitvector len=20
asicconfig = nexys.asicVector()

# Write to Asic

#Write zeros
dummyconfig=BitArray(uint=0, length=245)
dummybits = nexys.writeSRasic(dummyconfig, True)

#Write config
asicbits = nexys.writeSRasic(asicconfig, True)
nexys.write(dummybits+asicbits)

# Voltageboard
vdacbits = nexys.vbVector(4, [0.1, 0.2, 0.3, 0.4, 1, 0.6, 0.7, 0.8])

vbbits = nexys.writeSRgecco(12, vdacbits, 8)
nexys.write(vbbits)

nexys.close()
