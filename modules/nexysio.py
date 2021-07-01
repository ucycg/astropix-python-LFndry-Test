# -*- coding: utf-8 -*-
""""""
"""
Created on Fri Jun 25 16:10:45 2021

@author: Nicolas Striebig

"""
import ftd2xx as ftd

READ_ADRESS = 0x00
WRITE_ADRESS = 0x01

SR_ASIC_ADRESS = 0x00

SIN_ASIC = 0x04
LD_ASIC = 0x08

SIN_GECCO = 0x02
LD_GECCO = 0x04

NEXYS_USB = b'Digilent USB Device A'


class Nexysio:
    """Interface to Nexys FTDI Chip"""

    def __init__(self, handle=0) -> None:
        self.handle = handle
        #self.open_device(number)

    @classmethod
    def __addbytes(cls, value: bytearray, clkdiv: int) -> bytearray:

        data = bytearray()

        clkdiv = max(clkdiv, 1)

        for byte in value:
            data.extend(bytearray([byte]) * clkdiv)

        return data

    def open_device(self, number: int):
        """
        Opens the FTDI device

        :param number: Device index
        """

        self.handle = ftd.open(number)

        devinfo = self.handle.getDeviceInfo()

        if 'description' in devinfo and devinfo['description'] == NEXYS_USB:
            print("\u001b[32mDigilent USB A opened\n \u001b[0m")

            self.__setup()

            return self.handle
        else:
            self.close()

            raise NameError(f"Unknown Device with index {number}")

    def write(self, value: bytes) -> None:
        """Direct write to FTDI chip

        :param value: Bytestring to write
        """

        self.handle.write(value)

    def close(self) -> None:
        """Close connection"""

        self.handle.close()

    def __setup(self) -> None:
        """Set FTDI USB connection settings"""

        self.handle.setTimeouts(1000, 500)  # Timeout RX,TX
        self.handle.setBitMode(0xFF, 0x00)  # Reset
        self.handle.setBitMode(0xFF, 0x40)  # Set Synchronous 245 FIFO Mode
        self.handle.setLatencyTimer(2)
        self.handle.setUSBParameters(64000, 64000)  # Set Usb frame
        # self.handle.setDivisor(2)           # 60 Mhz Clock divider

    def write_register(self, register: int, value: int,
                       flush: bool = False) -> bytes:
        """Write Single Byte to Register

        :param register: FTDI Register to write
        :param value: Bytestring
        :param flush: Instant write
        """
        # print(f"Write Register {register} Value {hex(value)}")

        data = [WRITE_ADRESS, register, 0x00, 0x01, value]

        if flush:
            return self.handle.write(bytes(data))

        return bytes(data)

    def read_register(self, register: int) -> int:
        """Read Single Byte from Register

        :param register: FTDI Register to read from
        """

        self.handle.write(bytes([READ_ADRESS, register, 0x00, 0x01]))
        answer = self.handle.read(1)
        print(f"Read Register {register} Value 0x{answer.hex()}")

        return answer

    def write_gecco(self, address: int, value: bytearray,
                    clkdiv: int = 16) -> bytes:
        """Write to GECCO SR

        :param address: PCB register
        :param value: Bytearray vector
        :param clkdiv: Clockdivider 0-65535
        """

        # Number of Bytes to write
        length = (len(value) * 3 + 20) * clkdiv

        hbyte = length >> 8
        lbyte = length % 256

        header = bytearray([WRITE_ADRESS, address, hbyte, lbyte])

        print("\nWrite GECCO Config\n===============================")
        print(f"Length: {length} hByte: {hbyte} lByte: {lbyte}\n")
        print(f"Header: 0x{header.hex()}")
        print(f"Data ({len(value)} Bits): 0b{value.bin}\n")

        bit, data = 0, bytearray()

        # data
        for bit in value:

            pattern = SIN_GECCO if bit == 1 else 0

            data.extend([pattern, pattern | 1, pattern])

        # Load signal
        data.extend([LD_GECCO, 0x00])

        # Add 8 clocks
        data.extend([0x01, 0x00] * 8)

        data.extend([LD_GECCO, 0x00])

        data = self.__addbytes(data, clkdiv)

        # concatenate header+dataasic
        return b''.join([header, data])

    def write_asic(self, value: bytearray, wload: bool,
                   clkdiv: int = 16) -> bytes:
        """Write to ASIC SR

        :param value: Bytearray vector
        :param wload: Send load signal
        :param clkdiv: Clockdivider 0-65535
        """

        # Number of Bytes to write
        length = (len(value) * 5 + 30) * clkdiv

        hbyte = length >> 8
        lbyte = length % 256

        header = bytearray([WRITE_ADRESS, SR_ASIC_ADRESS, hbyte, lbyte])

        print("\nWrite Asic Config\n===============================")
        print(f"Length: {length} hByte: {hbyte} lByte: {lbyte}\n")
        print(f"Header: 0x{header.hex()}")
        print(f"Data ({len(value)} Bits): 0b{value.bin}\n")

        bit, data, load = 0, bytearray(), bytearray()

        # data
        for bit in value:

            pattern = SIN_ASIC if bit == 1 else 0

            # Generate double clocked pattern
            data.extend([pattern, pattern | 1, pattern, pattern | 2, pattern])

        # Load signal
        if wload:
            load.extend([0x00, LD_ASIC, 0x00])

        data = self.__addbytes(data, clkdiv)
        data.extend(self.__addbytes(load, clkdiv * 10))

        # concatenate header+data
        return b''.join([header, data])
