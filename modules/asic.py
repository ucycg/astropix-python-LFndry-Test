# -*- coding: utf-8 -*-
""""""
"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig

Astropix2 Configbits
"""
from bitstring import BitArray

from modules.nexysio import Nexysio


class Asic(Nexysio):
    """Configure ASIC"""

    def __init__(self, handle) -> None:

        self._handle = handle

        self.digitalconfig = {'interrupt_pushpull': 0}

        i = 1
        while i < 19:
            self.digitalconfig[f'En_Inj{i}'] = 0
            i += 1

        self.digitalconfig['ResetB'] = 0

        i = 0
        while i < 15:
            self.digitalconfig[f'Extrabit{i}'] = 0
            i += 1

        self.biasconfig = {
            'DisHiDR': 0,
            'q01': 0,
            'qon0': 0,
            'qon1': 1,
            'qon2': 0,
            'qon3': 1,
        }

        self.dacs = {
            'blres': 5,
            'nu1': 0,
            'vn1': 5,
            'vnfb': 10,
            'vnfoll': 1,
            'nu5': 0,
            'nu6': 0,
            'nu7': 0,
            'nu8': 0,
            'vn2': 0,
            'vnfoll2': 10,
            'vnbias': 20,
            'vpload': 1,
            'nu13': 0,
            'vncomp': 5,
            'vpfoll': 20,
            'nu16': 0,
            'vprec': 5,
            'vnrec': 5
        }

        self.recconfig = {'ColConfig0': 0b000_00000_00000_00000_00000_00000_00000_00000}
        self.recconfig['ColConfig1'] = 0b110_00000_00000_00000_00000_00000_00000_00001
        self.recconfig['ColConfig2'] = 0b000_00000_00000_00000_00000_00000_00000_00000
        self.recconfig['ColConfig3'] = 0b000_00000_00000_00000_00000_00000_00000_00000
        self.recconfig['ColConfig4'] = 0b000_00000_00000_00000_00000_00000_00000_00000
        self.recconfig['ColConfig5'] = 0b000_00000_00000_00000_00000_00000_00000_00000

        i = 6
        while i < 34:
            self.recconfig[f'ColConfig{i}'] = 0
            i += 1

        self.recconfig['ColConfig34'] = 0b000_00000_00000_00000_00000_00000_00000_00000

    @staticmethod
    def __int2nbit(value: int, nbits: int) -> BitArray:
        """Convert int to 6bit bitarray

        :param value: DAC value 0-63
        """

        try:
            return BitArray(uint=value, length=nbits)
        except ValueError:
            print(f'Allowed Dacvalues 0 - {2**nbits-1}')

    def gen_asic_vector(self, msbfirst: bool = False) -> BitArray:
        """Generate asic bitvector from digital, bias and dacconfig

        :param msbfirst: Send vector MSB first
        """

        bitvector = BitArray()

        for value in self.digitalconfig.values():
            bitvector.append(self.__int2nbit(value, 1))

        for value in self.biasconfig.values():
            bitvector.append(self.__int2nbit(value, 1))

        for value in self.dacs.values():
            bitvector.append(self.__int2nbit(value, 6))

        for value in self.recconfig.values():
            bitvector.append(self.__int2nbit(value, 38))

        if not msbfirst:
            bitvector.reverse()

        # print(f'Bitvector: {bitvector} \n')

        return bitvector

    def update_asic(self) -> None:
        """Update ASIC"""

        # Not needed for v2
        # dummybits = self.gen_asic_pattern(BitArray(uint=0, length=245), True)

        # Write config
        asicbits = self.gen_asic_pattern(self.gen_asic_vector(), True)
        self.write(asicbits)
