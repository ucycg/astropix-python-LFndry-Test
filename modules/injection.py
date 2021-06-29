# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 21:03:43 2021

@author: Nicolas Striebig
"""
from modules.nexysio import Nexysio

PG_RESET = 2
PG_SUSPEND = 3
PG_WRITE = 4
PG_OUTPUT = 5
PG_ADDRESS = 6
PG_DATA = 7


class Injection(Nexysio):
    """Sets injection setting for GECCO Injectionboard"""

    def __init__(self):
        self.period = 0
        self.cycle = 0
        self.clkdiv = 0
        self.initdelay = 0
        self.pulsesperset = 0

    def __patgenreset(self, reset: bool):
        return super().write_register(PG_RESET, reset)

    def __patgensuspend(self, suspend: bool):
        return super().write_register(PG_SUSPEND, suspend)

    @property
    def period(self):
        """Get/Set injection period"""

        return self._period

    @period.setter
    def period(self, period: int):
        if 0 <= period <= 255:
            self._period = period

    @property
    def cycle(self):
        """Get/Set injection #pulses"""

        return self._cycle

    @cycle.setter
    def cycle(self, cycle: int):
        if 0 <= cycle <= 65535:
            self._cycle = cycle

    @property
    def clkdiv(self):
        """Get/Set injection clockdivider"""

        return self._clkdiv

    @clkdiv.setter
    def clkdiv(self, clkdiv: int):
        if 0 <= clkdiv <= 65535:
            self._clkdiv = clkdiv

    @property
    def initdelay(self):
        """Get/Set injection initdelay"""

        return self._initdelay

    @initdelay.setter
    def initdelay(self, initdelay: int):
        if 0 <= initdelay <= 65535:
            self._initdelay = initdelay

    @property
    def pulsesperset(self):
        """Get/Set injection pulses/set"""

        return self._pulsesperset

    @pulsesperset.setter
    def pulsesperset(self, pulsesperset: int):
        if 0 <= pulsesperset <= 255:
            self._pulsesperset = pulsesperset

    def patgen(
            self, period: int,
            cycle: int,
            clkdiv: int,
            delay: int) -> bytearray:
        """Generate vector for injectionpattern"""

        data = bytearray()
        timestamps = [1, 3, 0, 0, 0, 0, 0, 0]

        for i, val in enumerate(timestamps):
            data.extend(self.patgenwrite(i, val))

        # Set period
        data.extend(self.patgenwrite(8, period))

        # Set flags
        data.extend(self.patgenwrite(9, 0b010100))

        # Set runlength
        data.extend(self.patgenwrite(10, cycle >> 8))
        data.extend(self.patgenwrite(11, cycle % 256))

        # Set initial delay
        data.extend(self.patgenwrite(12, delay >> 8))
        data.extend(self.patgenwrite(13, delay % 256))

        # Set clkdiv
        data.extend(self.patgenwrite(14, clkdiv >> 8))
        data.extend(self.patgenwrite(15, clkdiv % 256))

        return data

    def patgenwrite(self, address: int, value: int) -> bytearray:
        """Subfunction of patgen()"""

        data = bytearray()

        data.extend(super().write_register(PG_ADDRESS, address))
        data.extend(super().write_register(PG_DATA, value))
        data.extend(super().write_register(PG_WRITE, 1))
        data.extend(super().write_register(PG_WRITE, 0))

        return data

    def configureinjection(self):
        """Generate injection vector for set output, pattern and pulses/set"""

        print("\nWrite Injection Config\n===============================")

        output = super().write_register(PG_OUTPUT, 1)
        patgenconfig = self.patgen(
            self.period, self.cycle, self.clkdiv, self.initdelay)
        pulses = self.patgenwrite(7, self.pulsesperset)

        data = output+patgenconfig+pulses
        print(f"Injection vector({len(data)} Bytes): 0x{data.hex()}\n")

        return bytes(data)

    def start(self):
        """Start injection"""

        data = bytearray()

        data.extend(self.__patgensuspend(True))
        data.extend(self.__patgenreset(True))
        data.extend(self.__patgenreset(False))
        data.extend(self.__patgensuspend(False))

        print(f"Start inj({len(data)} Bytes): 0x{data.hex()}\n")
        return bytes(data)

    def stop(self):
        """Stop injection"""

        data = bytearray()

        data.extend(self.__patgensuspend(True))
        data.extend(self.__patgenreset(True))

        print(f"Stop inj({len(data)} Bytes): 0x{data.hex()}\n")
        return bytes(data)
