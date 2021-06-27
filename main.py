# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:10:56 2021

@author: nicolas
"""

from modules.gecco import gecco


nexys = gecco()

nexys.openDevice(0)

# Test Write and read
nexys.writeRegister(0x09, 0x55)
nexys.readRegister(0x09)

# Bitvector len=20
asicconfig = nexys.asicbitvector()

# Write to Asic
asicbits = nexys.writeSRasic(asicconfig, True)
#nexys.write(asicbits)



# Voltageboard
vdacbits = nexys.configVB(4, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])

vbbits = nexys.writeSRgecco(12, vdacbits, 8)
#nexys.write(vbbits)

nexys.close()
