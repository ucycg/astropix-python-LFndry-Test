# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig
"""
from bitstring import BitArray


class Genbitvector:
    """Generate bit patterns"""

    def __init__(self):

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
            'vncomp': 63,
            'nu30': 0,
            'nu31': 0,
            'nu32': 0,
            'nu33': 0,
        }

        self.vcal = 1

    @staticmethod
    def __inttobitvector_6b(value: int):
        """Convert int to 6bit bitarray"""

        try:
            vector = BitArray(uint=value, length=6)
        except TypeError:
            print("Allowed Dacvalues 0 - 63")

        return vector

    def asic_vector(self, msbfirst=False) -> BitArray:
        """Generate asic bitvector from digital, bias and dacconfig"""

        bitvector = BitArray()

        for value in self.digitalconfig.values():
            bitvector.append(BitArray(uint=value, length=1))

        for value in self.biasconfig.values():
            bitvector.append(BitArray(uint=value, length=1))

        for value in self.dacs.values():
            bitvector.append(self.__inttobitvector_6b(value))

        if not msbfirst:
            bitvector.reverse()

        return bitvector

    def vb_vector(self, pos: int, dacs: list) -> BitArray:
        """Generate VB bitvector from position and dacvalues"""

        vdacbits = BitArray()
        vdac = 0

        # Reverse List dacs
        dacs.reverse()

        for vdac in dacs:
            if not 0 <= vdac <= 1.8:
                print(
                    f"\u001b[31mDAC on VB{pos} {vdac}V not in range 0-1.8V\n\
                    -> Set to 0V \u001b[0m")

                vdac = 0

            dacvalue = int(vdac*16383/3.3/self.vcal)

            vdacbits.append(BitArray(uint=dacvalue, length=14))
            vdacbits.append(BitArray(uint=0, length=2))

        vdacbits.append(BitArray(uint=(0b10000000 >> (pos-1)), length=8))

        return vdacbits

    @property
    def vcal(self):
        """Property to get/set voltageboard calibration value\n
        Set DAC to 1V and write measured value to vcal
        """
        return self._vcal

    @vcal.setter
    def vcal(self, voltage: float):
        if 0.9 <= voltage <= 1.1:
            self._vcal = voltage

    def inj_vector(self):
        """Dummy"""

        pass
