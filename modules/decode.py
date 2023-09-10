# -*- coding: utf-8 -*-
""""""
"""
Created on Tue Dec 28 19:03:40 2021

@author: Nicolas Striebig
"""
import pandas as pd

import logging
from modules.setup_logger import logger


logger = logging.getLogger(__name__)


class Decode:
    def __init__(self, sampleclock_period_ns: int = 10, nchips: int = 1):
        self._sampleclock_period_ns = sampleclock_period_ns
        self._bytesperhit = 5
        self._idbits = 3
        self._nchips = nchips

        self._header = set()
        self._header_rev = set()
        self._gen_header()

    def _gen_header(self):
        """
        Pregenerate header bytes for nchips in a row
        """

        self._header = set()
        self._header_rev = set()

        for i in range(self._nchips):
            id = (i << self._idbits) + self._bytesperhit - 1
            self._header.add(id)

            id_rev = int(f'{id:08b}'[::-1], 2)
            self._header_rev.add(id_rev)

    def reverse_bitorder(self, data: bytearray) -> bytearray:
        reversed_data = bytearray()

        for item in data:
            item_rev = int(bin(item)[2:].zfill(8)[::-1], 2)
            reversed_data.append(item_rev)

        return reversed_data

    def hits_from_readoutstream(self, readout: bytearray, reverse_bitorder: bool = True) -> list:
        """
        Find hits in readoutstream

        :param readout: Readout stream
        :param reverse_bitorder: Reverse Bitorder per byte

        :returns: Position of hits in the datastream
        """

        length = len(readout)
        hitlist = []
        i = 0

        header = self._header_rev if reverse_bitorder else self._header
        bytesperhit = self._bytesperhit

        while i < length:
            if readout[i] not in header:
                i += 1
            else:
                if i + bytesperhit <= length:
                    if reverse_bitorder:
                        hitlist.append(self.reverse_bitorder(readout[i:i + bytesperhit]))
                    else:
                        hitlist.append(readout[i:i + bytesperhit])

                    i += bytesperhit
                else:
                    break

        return hitlist

    def decode_astropix2_hits(self, list_hits: list) -> pd.DataFrame:
        """
        Decode 5byte Frames from AstroPix 2

        Byte 0: Header      Bits:   7-3: ID
                                    2-0: Payload
        Byte 1: Location            7: Col
                                    6: reserved
                                    5-0: Row/Col
        Byte 2: Timestamp
        Byte 3: ToT MSB             7-4: 4'b0
                                    3-0: ToT MSB
        Byte 4: ToT LSB

        :param list_hists: List with all hits

        :returns: Dataframe with decoded hits
        """

        hit_pd = []

        for hit in list_hits:
            if len(hit) == self._bytesperhit:
                header, location, timestamp, tot_msb, tot_lsb = hit

                id          = header >> 3
                payload     = header & 0b111
                col         = location >> 7 & 1
                location   &= 0b111111
                timestamp   = timestamp
                tot_msb    &= 0b1111
                tot_total   = (tot_msb << 8) + tot_lsb

                hit_pd.append([id, payload, location, col, timestamp, tot_total])
                logger.info(
                    "Header: ChipId: %d\tPayload: %d\n"
                    "Location: %d\tRow/Col: %d\n"
                    "Timestamp: %d\n"
                    "ToT: MSB: %d\tLSB: %d Total: %d (%d us)",
                    id, payload, location, col, timestamp, tot_msb, tot_lsb, tot_total,
                    (tot_total * self._sampleclock_period_ns) / 1000.0
                )

        return pd.DataFrame(hit_pd, columns=['id', 'payload', 'location', 'col', 'timestamp', 'tot_total'])
