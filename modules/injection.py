# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 21:03:43 2021

@author: Nicolas Striebig
"""
from modules.nexysio import nexysio

PG_RESET = 2
PG_SUSPEND = 3
PG_WRITE = 4
PG_OUTPUT = 5
PG_ADDRESS = 6
PG_DATA = 7


class injection(nexysio):
    def __init__(self):
        self.period = 0
        self.cycle = 0
        self.clkdiv = 0
        self.initdelay = 0
        self.pulsesperset= 1

    def __patgenReset(self, reset: bool):
        return super(injection, self).writeRegister(PG_RESET, reset)

    def __patgenSuspend(self, suspend: bool):
        return super(injection, self).writeRegister(PG_SUSPEND, suspend)

    def patgenPeriod(self, period: int):
        self.period = period

    def patgenCycle(self, cycle: int):
        self.cycle = cycle

    def patgenClkdiv(self, clkdiv: int):
        self.clkdiv = clkdiv

    def patgenInitdelay(self, initdelay: int):
        self.initdelay = initdelay
        
    def patgenPulsesperset(self, pulsesperset: int):
        self.pulsesperset = pulsesperset

    def patgen(self, period: int, cycle: int, clkdiv: int, initdelay: int) -> bytearray:

        data = bytearray()
        timestamps = [1, 3, 0, 0, 0, 0, 0, 0]

        for i, val in enumerate(timestamps):
            data.extend(self.patgenWrite(i, val))

        # Period
        data.extend(self.patgenWrite(8, period))

        # Flags
        data.extend(self.patgenWrite(9, 0b010100))

        # runlength
        data.extend(self.patgenWrite(10, cycle >> 8))
        data.extend(self.patgenWrite(11, cycle % 256))

        # initial delay
        data.extend(self.patgenWrite(12, initdelay >> 8))
        data.extend(self.patgenWrite(13, initdelay % 256))

        # clkdiv
        data.extend(self.patgenWrite(14, clkdiv >> 8))
        data.extend(self.patgenWrite(15, clkdiv % 256))

        return data

    def patgenWrite(self, address: int, value: int) -> bytearray:

        data = bytearray()

        data.extend(super(injection, self).writeRegister(PG_ADDRESS, address))
        data.extend(super(injection, self).writeRegister(PG_DATA, value))
        data.extend(super(injection, self).writeRegister(PG_WRITE, 1))
        data.extend(super(injection, self).writeRegister(PG_WRITE, 0))

        return data

    def configureInjection(self):
        print("\nWrite Injection Config\n===============================")

        output = super(injection, self).writeRegister(PG_OUTPUT, 1)
        patgenconfig = self.patgen(
            self.period, self.cycle, self.clkdiv, self.initdelay)
        pulses = self.patgenWrite(7, self.pulsesperset)

        data = output+patgenconfig+pulses
        print("Injection vector({} Bytes): {}\n".format(len(data), data.hex()))

        return bytes(data)

    def start(self):

        data = bytearray()

        data.extend(self.__patgenSuspend(True))
        data.extend(self.__patgenReset(True))
        data.extend(self.__patgenReset(False))
        data.extend(self.__patgenSuspend(False))

        print("Start inj({} Bytes): {}\n".format(len(data), data.hex()))
        return bytes(data)

    def stop(self):

        data = bytearray()

        data.extend(self.__patgenSuspend(True))
        data.extend(self.__patgenReset(True))

        print("Stop inj({} Bytes): {}\n".format(len(data), data.hex()))
        return bytes(data)
