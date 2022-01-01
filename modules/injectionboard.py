# -*- coding: utf-8 -*-
""""""
"""
Created on Sun Jun 27 21:03:43 2021

@author: Nicolas Striebig
"""

import logging

from modules.nexysio import Nexysio
from modules.setup_logger import logger

PG_RESET    = 2
PG_SUSPEND  = 3
PG_WRITE    = 4
PG_OUTPUT   = 5
PG_ADDRESS  = 6
PG_DATA     = 7


logger = logging.getLogger(__name__)

class Injectionboard(Nexysio):
    """Sets injection setting for GECCO Injectionboard"""

    def __init__(self, handle) -> None:

        self._handle = handle

        self._period = 0
        self._cycle = 0
        self._clkdiv = 0
        self._initdelay = 0
        self._pulsesperset = 0

    def __patgenreset(self, reset: bool) -> bytes:
        return self.write_register(PG_RESET, reset)

    def __patgensuspend(self, suspend: bool) -> bytes:
        return self.write_register(PG_SUSPEND, suspend)

    def __patgen_write_register(self, pg_data: list, enum: bool = False):
        data = bytearray()

        if enum:
            for index, register_val in enumerate(pg_data):
                data.extend(self.write_register(index, register_val))
        else:
            for register in pg_data:
                data.extend(self.write_register(register[0], register[1]))

        return data

    @property
    def period(self) -> int:
        """Injection period"""

        return self._period

    @period.setter
    def period(self, period: int) -> None:
        if 0 <= period <= 255:
            self._period = period

    @property
    def cycle(self) -> int:
        """Injection #pulses"""

        return self._cycle

    @cycle.setter
    def cycle(self, cycle: int) -> None:
        if 0 <= cycle <= 65535:
            self._cycle = cycle

    @property
    def clkdiv(self) -> int:
        """Injection clockdivider"""

        return self._clkdiv

    @clkdiv.setter
    def clkdiv(self, clkdiv: int) -> None:
        if 0 <= clkdiv <= 65535:
            self._clkdiv = clkdiv

    @property
    def initdelay(self) -> int:
        """Injection initdelay"""

        return self._initdelay

    @initdelay.setter
    def initdelay(self, initdelay: int) -> None:
        if 0 <= initdelay <= 65535:
            self._initdelay = initdelay

    @property
    def pulsesperset(self) -> int:
        """Injection pulses/set"""

        return self._pulsesperset

    @pulsesperset.setter
    def pulsesperset(self, pulsesperset: int) -> None:
        if 0 <= pulsesperset <= 255:
            self._pulsesperset = pulsesperset

    def __patgen(self, period: int, cycle: int, clkdiv: int, delay: int) -> bytearray:
        """Generate vector for injectionpattern

        :param period: Set injection period 0-255
        :param cycle: Set injection cycle 0-65535
        :param clkdiv: Set injection clockdivider 0-65535
        :param delay: Set injection pulse delay 0-65535

        :returns: patgen vector
        """

        """ Bytes:
                0-7:    timestamps [1, 3, 0, 0, 0, 0, 0, 0]
                8:      period
                9:      flags 0b010100
                10:     cycle MSB
                11:     cycle LSB
                12:     delay MSB
                13:     delay LSB
                14:     clkdiv MSB
                15:     clkdiv LSB
        """

        pg_data = [1, 3, 0, 0, 0, 0, 0, 0, period, 0b010100, cycle >> 8, cycle % 256, delay >> 8, delay % 256, clkdiv >> 8, clkdiv % 256]

        return self.__patgen_write_register(pg_data, True)

    def __patgenwrite(self, address: int, value: int) -> bytearray:
        """Subfunction of patgen()

        :param address: Register address
        :param value: Value to append to writebuffer
        """

        pg_data = [(PG_ADDRESS, address), (PG_DATA, value), (PG_WRITE, 1), (PG_WRITE, 0)]

        return self.__patgen_write_register(pg_data)

    def __configureinjection(self) -> bytes:
        """
        Generate injection vector for set output, pattern and pulses/set

        :returns: config vector
        """

        logger.info("\nWrite Injection Config\n===============================")

        output = self.write_register(PG_OUTPUT, 1)
        patgenconfig = self.__patgen(self.period, self.cycle, self.clkdiv, self.initdelay)
        pulses = self.__patgenwrite(7, self.pulsesperset)

        data = output + patgenconfig + pulses
        logger.debug(f"Injection vector({len(data)} Bytes): 0x{data.hex()}\n")

        return bytes(data)

    def __start(self) -> bytes:
        """
        Start injection

        :returns: start vector
        """

        data = bytearray()

        data.extend(self.__patgensuspend(True))
        data.extend(self.__patgenreset(True))
        data.extend(self.__patgenreset(False))
        data.extend(self.__patgensuspend(False))

        logger.debug(f"Start inj({len(data)} Bytes): 0x{data.hex()}\n")

        return bytes(data)

    def __stop(self) -> bytes:
        """
        Stop injection

        :returns: stop vector
        """

        data = bytearray()

        data.extend(self.__patgensuspend(True))
        data.extend(self.__patgenreset(True))

        logger.debug(f"Stop inj({len(data)} Bytes): 0x{data.hex()}\n")

        return bytes(data)

    def update_inj(self) -> None:
        """Update injectionboard"""

        # Stop injection
        self.write(self.__stop())

        # Configure injection
        self.write(self.__configureinjection())

    def start(self) -> None:
        """Start injection"""

        # Stop injection
        self.write(self.__stop())

        # update inj
        self.update_inj()

        # Start Injection
        self.write(self.__start())

        logger.info("Start injection")

    def stop(self) -> None:
        """Stop injection"""

        self.write(self.__stop())

        logger.info("Stop injection")
