# -*- coding: utf-8 -*-
""""""
"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig
"""
from bitstring import BitArray

from modules.nexysio import Nexysio

# Set dac with less than 8 elements

class Voltageboard(Nexysio):

    def __init__(self, handle, pos, dacvalues):

        super().__init__(handle)

        self._pos = 0  # pos
        self._dacvalues = []  # dacvalues

        self._vcal = 1.0

        self.pos = pos
        self.dacvalues = dacvalues

    def __vb_vector(self, pos: int, dacs: list) -> BitArray:
        """Generate VB bitvector from position and dacvalues

        :param pos: Card slot
        :param dacs: List with DAC values
        """

        vdacbits = BitArray()

        # Reverse List dacs
        dacs = dacs[::-1]

        for vdac in dacs:

            dacvalue = int(vdac * 16383 / 3.3 / self.vcal)

            vdacbits.append(BitArray(uint=dacvalue, length=14))
            vdacbits.append(BitArray(uint=0, length=2))

        vdacbits.append(BitArray(uint=(0b10000000 >> (pos - 1)), length=8))

        return vdacbits

    @property
    def vcal(self) -> float:
        """Property to get/set voltageboard calibration value\n
        Set DAC to 1V and write measured value to vcal
        """
        return self._vcal

    @vcal.setter
    def vcal(self, voltage: float) -> None:
        if 0.9 <= voltage <= 1.1:
            self._vcal = voltage

    @property
    def dacvalues(self) -> list:
        """DAC voltages list"""
        return self._dacvalues

    @dacvalues.setter
    def dacvalues(self, dacvalues: tuple) -> None:

        length, values = dacvalues
        # If length > 8 strip values, if < 8 append 0
        values = values[:length] + [0] * (length - len(values))

        for index, value in enumerate(values):

            # If voltage out of range set 0
            if not 0 <= value <= 1.8:
                dacvalues[index] = 0

        self._dacvalues = values

        print(f"set dacvalues: {values}\n")

    @property
    def pos(self) -> int:
        """VB card position"""
        return self._pos

    @pos.setter
    def pos(self, pos) -> None:
        if 1 <= pos <= 8:
            self._pos = pos

    def update_vb(self) -> None:
        # Set and write
        # Set measured 1V for one-point calibration

        # Configure Voltageboard in Slot 4 with list values
        vdacbits = self.__vb_vector(self.pos, self.dacvalues)

        print(f'update_vb pos: {self.pos} value: {self.dacvalues}\n')

        # Generate pattern for Voltageboard Register 12 with clockdivider 8
        vbbits = super().write_gecco(12, vdacbits, 8)
        super().write(vbbits)
