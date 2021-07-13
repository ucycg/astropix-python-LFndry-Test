# -*- coding: utf-8 -*-
""""""
"""
Created on Tue Jul 12 20:07:13 2021

@author: Nicolas Striebig
"""
SIN_ASIC = 1

SPI_CONFIG = 0x15
SPI_CLKDIV = 0x16
"""
SPI_Config Register 21 (0x15)
0 	Write FIFO reset
1	Write FIFO empty flag (read-only)
2	Write FIFO full flag (read-only)
3	Read FIFO reset
4	Read FIFO empty flag (read-only)
5	Read FIFO full flag (read-only)
6	SPI Readback Enable
7	SPI module reset
"""


class Spi:
    def __init__(self):
        self._spi_clkdiv = 16

    def readout(self):
        pass

    @staticmethod
    def asic_spi_vector(value: bytearray, load: int,
                       clkdiv: int = 16) -> bytes:
        """
        Write ASIC config via SPI

        :param value: Bytearray vector
        :param load: Load signal
        :param clkdiv: Clockdivider 0-65535

        :returns: SPI ASIC config pattern
        """

        ck1 = 2
        ck2 = 4

        # Number of Bytes to write
        length = (len(value) * 5 + 30) * clkdiv

        print("\n SPI Write Asic Config\n===============================")
        print(f"Length: {length}\n")
        print(f"Data ({len(value)} Bits): {value}\n")

        bit, data = 0, bytearray()

        # data
        for bit in value:
            sin = SIN_ASIC if bit == 1 else 0
            # Generate double clocked pattern
            data.extend([sin, sin | ck1, sin, sin | ck2, sin])

        # Load signal
        i = 0
        if load:
            while i < 4:
                data.extend([sin | load])
                i += 1
            data.extend([sin])

        return data

    @property
    def spi_clkdiv(self):
        """SPI Clockdivider"""

        return self._spi_clkdiv

    @spi_clkdiv.setter
    def spi_clkdiv(self, clkdiv: int):

        self._spi_clkdiv
        if 0 <= clkdiv <= 65535:
            self.write_register(SPI_CLKDIV, clkdiv, True)

    def spi_enable(self, enable: bool):
        """
        Enable SPI

        Set SPI Reset bits to 0
        :param enable: Enable
        """

        if enable:
            self.write_register(SPI_CONFIG, 0x89, True)
            self.write_register(SPI_CONFIG, 0x12, True)

    def writenocheck(self, setting):
        config = bytearray()
        #config.extend([setting >> 16])
        #config.extend([setting >> 8])
        config.extend([setting])

        print(f'Writenocheck: {config}\n')
        return self.write_registers(23, config, False)

    def write_spi(self, data, pb, buffersize=1023):
        """
        Write to Nexys SPI Write FIFO

        :param data: Bytearray vector
        :param pb: Load signal
        :param buffersize: BUffersize
        """
        waiting = True
        counter = 1000

        # Check if WrFIFO is Empty
        while waiting & (counter > 0):
            counter -= 1

            # Convert Hex string to int
            result = int.from_bytes(self.read_register(SPI_CONFIG), 'big')

            # WrFIFOEmpty value
            compare = 2

            if (result & compare) != 0:
                waiting = False

        i = 0
        writebuffer = bytearray()

        counter = buffersize / 3

        while i < len(data):

            if counter > 0:
                print(f'print data[i]:{data[i]}\n')
                writebuffer += self.writenocheck(data[i])
                i += 1
                counter -= 1
                if (pb != 0) & ((i % 5) == 4):
                    print(f'Writebuffer: {writebuffer}\n')
                    self.write(bytes(writebuffer))
            else:
                result = int(self.read_register(SPI_CONFIG), base=16)

                # WrFIFOEmpty value
                compare_empty = 2
                compare_full = 4

                if (result & compare_empty) != 0:
                    counter = buffersize / 3
                elif (result & compare_full) == 0:
                    counter = 1
