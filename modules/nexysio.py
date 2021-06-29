# -*- coding: utf-8 -*-
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


class nexysio:

    # def __init__(self):
    #    self.handle=0

    def openDevice(self, number: int):

        self.handle = ftd.open(number)

        deviceinfo = self.handle.getDeviceInfo()

        if 'description' in deviceinfo and b'Digilent USB Device A' == deviceinfo['description']:
            print("\u001b[32mDigilent USB A opened\n \u001b[0m")

            self.__setup()
        else:
            self.close()

            raise NameError(f"Unknown Device with index {number}")

    def write(self, value: bytes):
        self.handle.write(value)

    def close(self):
        self.handle.close()

    def __AddBytes(self, value: int, clkdiv: int) -> bytearray:

        data = bytearray()

        if clkdiv < 1:
            clkdiv = 1

        for byte in value:
            data.extend(bytearray([byte])*clkdiv)

        return data

    def __setup(self):
        """Set FTDI setting with int value from 0 to 63"""

        self.handle.setTimeouts(1000, 500)  # Timeout RX,TX
        self.handle.setBitMode(0xFF, 0x00)  # Reset
        self.handle.setBitMode(0xFF, 0x40)  # Set Synchronous 245 FIFO Mode
        self.handle.setLatencyTimer(2)
        self.handle.setUSBParameters(64000, 64000)  # Set Usb frame
        # self.handle.setDivisor(2)           # 60 Mhz Clock divider

    def writeRegister(self, register: int, value: int, flush=False):
        """Write Single Byte to Register

        Attributes:
            register     FTDI Register to write
            value        Bytestring
        """
        if flush:
            return self.handle.write(bytes([WRITE_ADRESS, register, 0x00, 0x01, value]))
        else:
            return bytes([WRITE_ADRESS, register, 0x00, 0x01, value])
        print(f"Write Register {register} Value {hex(value)}")

    def readRegister(self, register: int) -> int:
        """Write Single Byte to Register

        Attributes:
            register     FTDI Register to read
        """

        self.handle.write(bytes([READ_ADRESS, register, 0x00, 0x01]))
        answer = self.handle.read(1)
        print("Read Register {register} Value 0x{answer.hex()}")

        return answer

    def writeSRgecco(self, address: int, value: bytearray, clkdiv=16) -> bytes:
        """Write to GECCO SR"""

        # Number of Bytes to write
        length = (len(value)*3+20)*clkdiv

        hByte = int(length/256)
        lByte = length % 256

        header = bytearray([WRITE_ADRESS, address, hByte, lByte])

        print("\nWrite GECCO Config\n===============================")
        print(f"Length: {length} hByte: {hByte} lByte: {lByte}\n")
        print(f"Header: 0x{header.hex()}")
        print(f"Data ({len(value)} Bits): 0b{value.bin}\n")

        bit, data = 0, bytearray()

        # data
        for bit in value:
            if bit == 1:
                pattern = SIN_GECCO
            else:
                pattern = 0

            data.extend([pattern, pattern | 1, pattern])

        # Load signal
        data.extend([LD_GECCO, 0x00])

        i = 0
        while i < 8:
            data.extend([0x01, 0x00])
            i += 1

        data.extend([LD_GECCO, 0x00])

        data = self.__AddBytes2(data, clkdiv)

        # concatenate header+dataasic
        return b''.join([header, data])

    def writeSRasic(self, value: bytearray, sendload: bool, clkdiv=16) -> bytes:
        """Write to ASIC SR"""

        # Number of Bytes to write
        length = (len(value)*5+30)*clkdiv

        hByte = int(length/256)
        lByte = length % 256

        header = bytearray([WRITE_ADRESS, SR_ASIC_ADRESS, hByte, lByte])

        print("\nWrite Asic Config\n===============================")
        print(f"Length: {length} hByte: {hByte} lByte: {lByte}\n")
        print(f"Header: 0x{header.hex()}")
        print(f"Data ({len(value)} Bits): 0b{value.bin}\n")

        bit, data, load = 0, bytearray(), bytearray()

        # data
        for bit in value:

            if bit == 1:
                pattern = SIN_ASIC
            else:
                pattern = 0

            # Generate double clocked pattern
            data.extend([pattern, pattern | 1, pattern, pattern | 2, pattern])

        # Load signal
        if sendload:
            load.extend([0x00, LD_ASIC, 0x00])

        data = self.__AddBytes2(data, clkdiv)
        data.extend(self.__AddBytes2(load, clkdiv*10))

        # concatenate header+data
        return b''.join([header, data])
