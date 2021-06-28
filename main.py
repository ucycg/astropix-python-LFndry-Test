# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:10:56 2021

@author: Nicolas Striebig
"""

from modules.gecco import gecco
from modules.injection import injection

from bitstring import BitArray

nexys = gecco()

# Open FTDI Device with Index 0
nexys.openDevice(0)

# Write 0x55 to register 0x09 and read it back
nexys.writeRegister(0x09, 0x55, True)
nexys.readRegister(0x09)

# Generate pattern for asicSR
asicconfig = nexys.asicVector()

# Write to Asic

# Write zeros
dummyconfig = BitArray(uint=0, length=245)
dummybits = nexys.writeSRasic(dummyconfig, True)

# Write config
asicbits = nexys.writeSRasic(asicconfig, True)
nexys.write(dummybits+asicbits)

# Configure Voltageboard

# Configure Voltageboard in Slot 4 with list values
vdacbits = nexys.vbVector(4, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])

# Generate pattern for Voltageboard Register 12 with clockdivider 8
vbbits = nexys.writeSRgecco(12, vdacbits, 8)
nexys.write(vbbits)

# Configure Injection

# Set Injection level
injdacbits = nexys.writeSRgecco(12, nexys.vbVector(5, [1, 1]), 8)
nexys.write(injdacbits)

inj = injection()

# Set Injection Params
inj.patgenPeriod(100)
inj.patgenClkdiv(300)
inj.patgenInitdelay(200)
inj.patgenCycle(0)
inj.patgenPulsesperset(1)

# Stop injection
stopinj = inj.stop()
nexys.write(stopinj)

# Configure injection
injvector = inj.configureInjection()
nexys.write(injvector)

# Start Injection
startinj = inj.start()
nexys.write(startinj)

# Close connection
nexys.close()
