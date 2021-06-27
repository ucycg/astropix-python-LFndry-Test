# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 16:10:45 2021

@author: nicolas

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

    def __AddBytes(self, value: int, clkdiv: int) -> bytes:

        if clkdiv < 1:
            clkdiv = 1

        return bytes([value]*clkdiv)

    def __setup(self):
        """Set FTDI setting with int value from 0 to 63"""

        self.handle.setTimeouts(1000, 500)  # Timeout RX,TX
        self.handle.setBitMode(0xFF, 0x00)  # Reset
        self.handle.setBitMode(0xFF, 0x40)  # Set Synchronous 245 FIFO Mode
        self.handle.setLatencyTimer(2)
        self.handle.setUSBParameters(64000, 64000)  # Set Usb frame
        #self.handle.setDivisor(2)           # 60 Mhz Clock divider

    def writeRegister(self, register: int, value: int):
        """Write Single Byte to Register
        
        Attributes:
            register     FTDI Register to write
            value        Bytestring
        """

        self.handle.write(bytes([WRITE_ADRESS, register, 0x00, 0x01, value]))
        print("Write Register {} Value {}".format(register, hex(value)))

    def readRegister(self, register: int) -> int:
        """Write Single Byte to Register
        
        Attributes:
            register     FTDI Register to read
        """
        
        self.handle.write(bytes([READ_ADRESS, register, 0x00, 0x01]))
        answer = self.handle.read(1)
        print("Read Register {} Value 0x{}".format(register, answer.hex()))

        return answer
    
    def writeSRgecco(self, address: int, value: bytes, clkdiv=16) -> bytes:
        """Write to GECCO SR"""

        # Number of Bytes to write
        length = (len(value)*3+20)*clkdiv

        hByte = int(length/256)
        lByte = length % 256

        header = bytes([WRITE_ADRESS, address, hByte, lByte])

        print("\nWrite GECCO Config\n===============================")
        print("Length: {} hByte: {} lByte: {}\n".format(length, hByte, lByte))
        print("Header: {}".format(header.hex()))
        print("Data ({} Bits): {}\n".format(len(value), value.bin))

        bit, data = 0, bytes()

        # data
        for bit in value:

            if bit == 1:
                pattern = SIN_GECCO
            else:
                pattern = 0

            # Generate double clocked pattern
            b"".join([data, self.__AddBytes(pattern, clkdiv)])
            b"".join([data, self.__AddBytes(pattern | 1, clkdiv)])
            b"".join([data, self.__AddBytes(pattern, clkdiv)])

        # Load signal
        b"".join([data, self.__AddBytes(LD_GECCO, clkdiv)])
        b"".join([data, self.__AddBytes(0x00, clkdiv)])

        i = 0
        while i < 8:
            b"".join([data, self.__AddBytes(0x01, clkdiv)])
            b"".join([data, self.__AddBytes(0x00, clkdiv)])
            i += 1

        b"".join([data, self.__AddBytes(LD_GECCO, clkdiv)])
        b"".join([data, self.__AddBytes(0x00, clkdiv)])

        # concencate header+dataasic

        return header+data
    
    def writeSRasic(self, value: bytes, sendload: bool, clkdiv=16) -> bytes:
        """Write to ASIC SR"""

        # Number of Bytes to write
        length = (len(value)*5+30)*clkdiv

        hByte = int(length/256)
        lByte = length % 256

        header = bytes([WRITE_ADRESS, SR_ASIC_ADRESS, hByte, lByte])

        print("\nWrite Asic Config\n===============================")
        print("Length: {} hByte: {} lByte: {}\n".format(length, hByte, lByte))
        print("Header: {}".format(header.hex()))
        print("Data ({} Bits): {}\n".format(len(value), value.bin))

        bit, data = 0, bytes()

        # data
        for bit in value:

            if bit == 1:
                pattern = SIN_ASIC
            else:
                pattern = 0

            # Generate double clocked pattern
            b"".join([data,self.__AddBytes(pattern, clkdiv)])
            b"".join([data,self.__AddBytes(pattern | 1, clkdiv)])
            b"".join([data,self.__AddBytes(pattern, clkdiv)])
            b"".join([data,self.__AddBytes(pattern | 2, clkdiv)])
            b"".join([data,self.__AddBytes(pattern, clkdiv)])

        # Load signal
        if sendload:
            b"".join([data,self.__AddBytes(0x00, 10*clkdiv)])
            b"".join([data,self.__AddBytes(LD_ASIC, 10*clkdiv)])
            b"".join([data,self.__AddBytes(0x00, 10*clkdiv)])

        # concencate header+data

        return header+data
