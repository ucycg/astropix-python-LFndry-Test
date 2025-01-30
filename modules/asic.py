# -*- coding: utf-8 -*-
""""""
"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig (Original Author), Justin Cott (Contributor)

Functions for ASIC configuration
"""
import logging
import yaml
from bitstring import BitArray

from modules.nexysio import Nexysio
from modules.setup_logger import logger


logger = logging.getLogger(__name__)

COLCONFIG_MASK_ALL = 0b001_11111_11111_11111_11111_11111_11111_11110
COLCONFIG_MASK_ROW = 0b111_11111_11111_11111_11111_11111_11111_11110
COLCONFIG_MASK_COL = 0b101_11111_11111_11111_11111_11111_11111_11111
COLCONFIG_MASK_AMP = 0b011_11111_11111_11111_11111_11111_11111_11111


class Asic(Nexysio):
    """Configure ASIC"""

    def __init__(self, handle) -> None:

        self._handle = handle

        self._chipversion = None

        self._num_rows = 35
        self._num_cols = 35

        self.asic_config = {}
        self.asic_tdac_config = {}

        self._num_chips = 1             # is this correct?

        self._chipname = ""

    @property
    def chipname(self):
        """Get/set chipname

        :returns: chipname
        """
        return self._chipname

    @chipname.setter
    def chipname(self, chipname):
        self._chipname = chipname

    @property
    def chipversion(self):
        """Get/set chipversion

        :returns: chipversion
        """
        return self._chipversion

    @chipversion.setter
    def chipversion(self, chipversion):
        self._chipversion = chipversion

    @property
    def chip(self):
        """Get/set chip+version

        :returns: chipname
        """
        return self.chipname + str(self.chipversion)

    @property
    def num_cols(self):
        """Get/set number of columns

        :returns: Number of columns
        """
        return self._num_cols

    @num_cols.setter
    def num_cols(self, cols):
        self._num_cols = cols

    @property
    def num_rows(self):
        """Get/set number of rows

        :returns: Number of rows
        """
        return self._num_rows

    @num_rows.setter
    def num_rows(self, rows):
        self._num_rows = rows

    @property
    def num_chips(self):
        """Get/set number of chips in telescope setup

        :returns: Number of chips in telescope setup
        """
        return self._num_chips

    @num_chips.setter
    def num_chips(self, chips):
        self._num_chips = chips

    def enable_inj_row(self, row: int):
        """Enable Row injection switch

        :param row: Row number
        """
        self.set_inj_row(row, True)
        print("enable_inj_row() and disable_inj_row() are deprecated use set_inj_row()")

    def disable_inj_row(self, row: int):
        """Disable row injection switch

        :param row: Row number
        """
        self.set_inj_row(row, False)
        print("enable_inj_row() and disable_inj_row() are deprecated use set_inj_row()")

    def enable_inj_col(self, col: int):
        """Enable col injection switch

        :param col: Col number
        """
        self.set_inj_col(col, True)
        print("enable_inj_col() and disable_inj_col() are deprecated use set_inj_col()")

    def disable_inj_col(self, col: int):
        """Disable col injection switch

        :param col: Col number
        """
        self.set_inj_col(col, False)
        print("enable_inj_col() and disable_inj_col() are deprecated use set_inj_col()")

    def enable_ampout_col(self, col: int):
        """Select Col for analog mux and disable other cols

        :param col: Col number
        """
        for i in range(self.num_cols):
            self.asic_config['recconfig'][f'col{i}'][1] &= COLCONFIG_MASK_AMP

        self.asic_config['recconfig'][f'col{col}'][1] |= 1 << 37

    def enable_pixel(self, col: int, row: int):
        """Enable pixel comparator for specified pixel

        :param col: Col number
        :param row: Row number
        """
        self.set_pixel_comparator(col, row, True)
        print("enable_pixel() and disable_pixel() are deprecated use set_pixel_comparator()")

    def disable_pixel(self, col: int, row: int):
        """Disable pixel comparator for specified pixel

        :param col: Col number
        :param row: Row number
        """
        self.set_pixel_comparator(col, row, False)
        print("enable_pixel() and disable_pixel() are deprecated use set_pixel_comparator()")

    def set_pixel_comparator(self, col: int, row: int, enable: bool):
        """Enable or disable pixel comparator for specified pixel

        :param col: Col number
        :param row: Row number
        :param enable: True to enable, False to disable
        """
        if row < self.num_rows and col < self.num_cols:
            if enable:
                self.asic_config['recconfig'][f'col{col}'][1] &= ~(2 << row)
            else:
                self.asic_config['recconfig'][f'col{col}'][1] |= (2 << row)

    def set_inj_row(self, row: int, enable: bool):
        """Enable or disable row injection switch

        :param row: Row number
        :param enable: True to enable, False to disable
        """
        if row < self.num_rows:
            if enable:
                self.asic_config['recconfig'][f'col{row}'][1] |= 1 << 0
            else:
                self.asic_config['recconfig'][f'col{row}'][1] &= COLCONFIG_MASK_ROW

    def set_inj_col(self, col: int, enable: bool):
        """Enable or disable col injection switch

        :param col: Col number
        :param enable: True to enable, False to disable
        """
        if col < self.num_cols:
            if enable:
                self.asic_config['recconfig'][f'col{col}'][1] |= 1 << 36
            else:
                self.asic_config['recconfig'][f'col{col}'][1] &= COLCONFIG_MASK_COL

    def get_pixel(self, col: int, row: int) -> bool:
        """Check if Pixel is enabled

        :param col: Col number
        :param row: Row number
        """
        if row < self.num_rows:
            return not bool(self.asic_config['recconfig'].get(f'col{col}')[1] & (1 << (row + 1)))

        logger.error("Invalid row %d larger than %d", row, self.num_rows)
        return None

    def reset_recconfig(self):
        """Reset recconfig to default mask"""
        for key in self.asic_config['recconfig']:
            self.asic_config['recconfig'][key][1] = COLCONFIG_MASK_ALL

    def set_internal_vdac(self, dac: str, voltage: float, vdda: float = 1.8, nbits: int = 10) -> None:
        """Set integrated VDAC voltage

        :param dac: Name of dac
        :param voltage: Voltage from 0 to 1.8
        :param vdd: Supply voltage VDDA
        :param nbits: VDAC resolution
        """
        if dac in self.asic_config['vdacs'] and 0 <= voltage <= 1.8:
            dacval = voltage * vdda / 2**nbits
            self.asic_config['vdacs'][dac] = dacval
            logger.debug('Set internal vdac: %s to %d V (dacval: %d)', dac, voltage, dacval)
        else:
            logger.warning('Can not set internal vdac: %s to %d V!', dac, voltage)

    @staticmethod
    def __int2nbit(value: int, nbits: int) -> BitArray:
        """Convert int to 6bit bitarray

        :param value: Integer value
        :param nbits: Number of bits

        :returns: Bitarray of specified length
        """

        try:
            return BitArray(uint=value, length=nbits)
        except ValueError:
            logger.error('Allowed Values 0 - %d', 2**nbits - 1)
            return None

    def load_conf_from_yaml(self, chipversion: int, filename: str, **kwargs) -> None:
        """Load ASIC config from yaml

        :param chipversion: Name of yml file in config folder     
        :param filename: Name of yml file in config folder
        :param chipname; Name of the chip i.e. astropix
        """
        #DO I introduce a Bug, because my chipversion (1) is not part of yml file name?
        chipname = kwargs.get('chipname', 'astropix_lf_test')

        self.chipversion = chipversion
        self.chipname = chipname

        with open(f"config/{filename}.yml", "r", encoding="utf-8") as stream:
            try:
                dict_from_yml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

        # Get Telescope settings
        try:
            self.num_chips = dict_from_yml[self.chip].get('telescope')['nchips']

            logger.info("%s%d Telescope setup with %d chips found!", chipname, chipversion, self.num_chips)
        except (KeyError, TypeError):
            logger.warning("%s%d Telescope config not found!", chipname, chipversion)

        # Get chip geometry
        try:
            self.num_cols = dict_from_yml[self.chip].get('geometry')['cols']
            self.num_rows = dict_from_yml[self.chip].get('geometry')['rows']

            logger.info("%s%d matrix dimensions found!", chipname, chipversion)
        except KeyError:
            logger.error("%s%d matrix dimensions not found!", chipname, chipversion)
            raise

        # Get chip configs
        if self.num_chips > 1:
            for chip_number in range(self.num_chips):
                try:
                    self.asic_config[f'config_{chip_number}'] = dict_from_yml.get(self.chip)[f'config_{chip_number}']
                    logger.info("Telescope chip_%d config found!", chip_number)
                except KeyError:
                    logger.error("Telescope chip_%d config not found!", chip_number)
                    raise
        else:
            try:
                self.asic_config = dict_from_yml.get(self.chip)['config']
                logger.info("%s%d config found!", chipname, chipversion)
            except KeyError:
                logger.error("%s%d config not found!", chipname, chipversion)
                raise

        # Get chip tdac configs
        if self.num_chips > 1:
            for chip_number in range(self.num_chips):
                try:
                    self.asic_tdac_config[f'tdac_config_{chip_number}'] = dict_from_yml.get(self.chip)[f'tdac_config_{chip_number}']
                    logger.info("Telescope chip_%d tdac config found!", chip_number)
                except KeyError:
                    logger.error("Telescope chip_%d tdac config not found!", chip_number)
                    raise
        else:
            try:
                self.asic_tdac_config = dict_from_yml.get(self.chip)['tdac_config']
                logger.info("%s%d tdac config found!", chipname, chipversion)
            except KeyError:
                logger.error("%s%d tdac config not found!", chipname, chipversion)
                raise

    def write_conf_to_yaml(self, filename: str) -> None:
        """Write ASIC config to yaml

        :param filename: Name of yml file in config folder
        """
        dicttofile = {
            self.chip:
                {
                    "telescope": {"nchips": self.num_chips},
                    "geometry": {"cols": self.num_cols, "rows": self.num_rows}
                }
        }

        if self.num_chips > 1:
            for chip in range(self.num_chips):
                dicttofile[self.chip][f'config_{chip}'] = self.asic_config[f'config_{chip}']
        else:
            dicttofile[self.chip]['config'] = self.asic_config

        with open(f"config/{filename}.yml", "w", encoding="utf-8") as stream:
            try:
                yaml.dump(dicttofile, stream, default_flow_style=False, sort_keys=False)

            except yaml.YAMLError as exc:
                logger.error(exc)

    def gen_asic_vector(self, msbfirst: bool = False) -> BitArray:
        """Generate asic bitvector from digital, bias and dacconfig

        :param msbfirst: Send vector MSB first
        """

        bitvector = BitArray()

        if self.num_chips > 1:
            for chip in range(self.num_chips - 1, -1, -1):

                for key in self.asic_config[f'config_{chip}']:
                    for values in self.asic_config[f'config_{chip}'][key].values():
                        bitvector.append(self.__int2nbit(values[1], values[0]))

                if not msbfirst:
                    bitvector.reverse()

                logger.info("Generated chip_%d config successfully!", chip)

        else:
            for key in self.asic_config:
                for values in self.asic_config[key].values():
                    if key == 'vdacs':
                        bitvector2 = BitArray(self.__int2nbit(values[1], values[0]))
                        bitvector2.reverse()
                        bitvector.append(bitvector2)
                    else:
                        bitvector.append(self.__int2nbit(values[1], values[0]))

            if not msbfirst:
                bitvector.reverse()

        return bitvector

    def gen_asic_row_vector(self, row: int, msbfirst: bool = False, ) -> BitArray:
        """Generate asic tdac bitvector

        :param row: Specify row to write tdac config
        :param msbfirst: Send vector MSB first
        """
        bitvector = BitArray()

        if self.num_chips > 1:
            for chip in range(self.num_chips - 1, -1, -1):
                bitvector.append(self.__int2nbit(self.asic_tdac_config[f'config_{chip}'][f'row{row}'][1],
                                                 self.asic_tdac_config[f'config_{chip}'][f'row{row}'][0]))

                if not msbfirst:
                    bitvector.reverse()

                logger.info("Generated chip_%d tdac config successfully!", chip)

        else:
            bitvector.append(self.__int2nbit(self.asic_tdac_config[f'row{row}'][1],
                                             self.asic_tdac_config[f'row{row}'][0]))

            if not msbfirst:
                bitvector.reverse()

        return bitvector

    def update_asic(self) -> None:
        """Update ASIC"""

        # THIS HAS NOTHING TO DO WITH JUSTINS ASTROPIX LF TST CHIP
        #if self.chipversion == 1:
        #    dummybits = self.gen_asic_pattern(BitArray(uint=0, length=245), True)  # Not needed for v2
        #    self.write(dummybits)

        # Write config
        asicbits = self.gen_asic_pattern(self.gen_asic_vector(), True)

        for value in asicbits:
            self.write(value)

    def update_asic_tdacrow(self, row: int) -> None:
        """Write ASIC TDAC ROW
        :param row: Specify row to write tdac config
        """
        asicbits = self.gen_tdac_pattern(self.gen_asic_row_vector(row), True)

        self.write(asicbits)

    def readback_asic(self):
        asicbits = self.gen_asic_pattern(self.gen_asic_vector(), True, readback_mode=True)
        print(asicbits)
        self.write(asicbits)
