# -*- coding: utf-8 -*-
""""""
"""
Created on Tue Jul 12 20:07:13 2021

@author: Nicolas Striebig
"""
from time import sleep

#SIN_ASIC = 1
SPI_SR_CMD = 0x30

SPI_SR_SIN = 0x80
SPI_SR_LD = 0xff

SPI_CONFIG = 0x15
SPI_CLKDIV = 0x16

SPI_WRITE_REG = 23
SPI_READ_REG = 24


class Spi:
    """
    Nexys SPI Communication

    Registers:
    | SPI_Config Register 21 (0x15)
        | 0 	Write FIFO reset
        | 1	Write FIFO empty flag (read-only)
        | 2	Write FIFO full flag (read-only)
        | 3	Read FIFO reset
        | 4	Read FIFO empty flag (read-only)
        | 5	Read FIFO full flag (read-only)
        | 6	SPI Readback Enable
        | 7	SPI module reset
    | SPI_CLKDIV Register 22
    | SPI_Write Register 23
    | SPI_Read Register 24
    """
    def __init__(self):
        self._spi_clkdiv = 16

    def readout(self):
        pass

    @staticmethod
    def set_bit(value, bit):
        return value | (1 << bit)

    @staticmethod
    def clear_bit(value, bit):
        return value & ~(1 << bit)

    @staticmethod
    def asic_spi_vector(value: bytearray, load: int) -> bytes:
        """
        Write ASIC config via SPI

        :param value: Bytearray vector
        :param load: Load signal

        :returns: SPI ASIC config pattern
        """

        ck1 = 2
        ck2 = 4

        # Number of Bytes to write
        length = len(value) * 5 + 4

        print("\n SPI Write Asic Config\n===============================")
        print(f"Length: {length}\n")
        print(f"Data ({len(value)} Bits): {value}\n")

        # Write SPI SR Command to set MUX
        data = bytearray([SPI_SR_CMD])

        # data
        for bit in value:
            sin = SPI_SR_SIN if bit == 1 else 0

            data.extend([sin])

        # Load signal
        i = 0
        if load:
            while i < 4:
                data.extend([SPI_SR_LD])
                i += 1

        return data

    @property
    def spi_clkdiv(self):
        """SPI Clockdivider"""

        return self._spi_clkdiv

    @spi_clkdiv.setter
    def spi_clkdiv(self, clkdiv: int):

        if 0 <= clkdiv <= 65535:
            self._spi_clkdiv = clkdiv
            self.write_register(SPI_CLKDIV, clkdiv, True)

    def spi_enable(self):
        """
        Enable SPI by setting reset bits low

        Set SPI Reset bits to 0
        """
        configregister = int.from_bytes(self.read_register(SPI_CONFIG), 'big')

        set_bits = [0, 3, 7]
        clear_bits = [0, 3, 6, 7]

        # Set Reset bits 1
        for bit in set_bits:
            configregister = self.set_bit(configregister, bit)

        # Set Reset bits and readback bit 0
        for bit in clear_bits:
            configregister = self.clear_bit(configregister, bit)

        # Write new values
        self.write_register(SPI_CONFIG, configregister, True)

    def direct_write_spi(self, data: bytes) -> None:
        """
        Direct write to SPI Write Register

        :param data: Data
        """
        self.write_registers(SPI_WRITE_REG, data, True)

    def read_spi(self, num: int):

        return self.read_register(SPI_READ_REG, num)

    def write_spi(self, data: bytearray, buffersize=1023) -> None:
        """
        Write to Nexys SPI Write FIFO

        :param data: Bytearray vector
        :param buffersize: BUffersize
        """
        waiting = True
        counter = 1000

        # Check if WrFIFO is Empty
        while waiting: #& (counter > 0):
            #counter -= 1

            # Convert Hex string to int
            result = int.from_bytes(self.read_register(SPI_CONFIG), 'big')

            # WrFIFOEmpty value
            compare = 2

            if (result & compare) != 0:
                waiting = False
            else:
                sleep(0.002)

        i = 0
        writebuffer = bytearray()

        counter = buffersize / 3

        while i < len(data):

            if counter > 0:
                print(f'print data[i]:{data[i]}\n')
                # writebuffer += self.direct_write_spi(data[i])

                writebuffer += bytearray([data[i]])

                i += 1
                counter -= 1
                if (i % 5) == 4:
                    print(f'Writebuffer: {writebuffer}\n')
                    self.direct_write_spi(bytes(writebuffer))
                    writebuffer = bytearray()

            else:
                result = int.from_bytes(self.read_register(SPI_CONFIG), 'big')

                # WrFIFOEmpty value
                compare_empty = 2
                compare_full = 4

                if (result & compare_empty) != 0:
                    counter = buffersize / 3
                elif (result & compare_full) == 0:
                    counter = 1
