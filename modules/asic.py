# -*- coding: utf-8 -*-
""""""
"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig
"""
from bitstring import BitArray

from modules.nexysio import Nexysio


class Asic(Nexysio):
    """Configure ASIC"""

    def __init__(self, handle) -> None:

        self._handle = handle

        self.digitalconfig = {'interrupt_pushpull': 0,
                              'ResetB Biasblock': 0}

        i = 1
        while i < 19:
            self.digitalconfig[f'En_Inj{i}'] = 0
            i += 1

        i = 0
        while i < 15:
            self.digitalconfig[f'Extrabit{i}'] = 0
            i += 1

        self.biasconfig = {
            'q00': 0,
            'q01': 0,
            'qon0': 0,
            'qon1': 1,
            'qon2': 0,
            'qon3': 1,
        }

        self.dacs = {
            'blres': 5,
            'nu1': 0,
            'vn1': 2,
            'vnfb': 5,
            'vnfoll': 1,
            'nu5': 0,
            'nu6': 0,
            'nu7': 0,
            'nu8': 0,
            'vn2': 0,
            'vnfoll2': 5,
            'vnbias': 5,
            'vpload': 1,
            'nu13': 0,
            'nu14': 0,
            'nu15': 0,
            'nu16': 0,
            'nu17': 0,
            'nu18': 0,
            'nu19': 0,
            'nu20': 0,
            'nu21': 0,
            'nu22': 0,
            'nu23': 0,
            'nu24': 0,
            'nu25': 0,
            'nu26': 0,
            'nu27': 0,
            'nu28': 0,
            'vncomp': 0,
            'nu30': 0,
            'nu31': 0,
            'nu32': 0,
            'nu33': 0,
        }

    @staticmethod
    def __intto6bit(value: int) -> BitArray:
        """Convert int to 6bit bitarray

        :param value: DAC value 0-63
        """

        try:
            return BitArray(uint=value, length=6)
        except ValueError:
            print("Allowed Dacvalues 0 - 63")

    def gen_asic_vector(self, msbfirst: bool = False) -> BitArray:
        """Generate asic bitvector from digital, bias and dacconfig

        :param msbfirst: Send vector MSB first
        """

        bitvector = BitArray()

        for value in self.digitalconfig.values():
            bitvector.append(BitArray(uint=value, length=1))

        for value in self.biasconfig.values():
            bitvector.append(BitArray(uint=value, length=1))

        for value in self.dacs.values():
            bitvector.append(self.__intto6bit(value))

        if not msbfirst:
            bitvector.reverse()

        return bitvector

    def update_asic(self) -> None:
        """Update ASIC"""

        # Write 245 zeros
        dummybits = self.gen_asic_pattern(BitArray(uint=0, length=245), True)

        # Write config
        asicbits = self.gen_asic_pattern(self.gen_asic_vector(), True)
        self.write(dummybits + asicbits)
