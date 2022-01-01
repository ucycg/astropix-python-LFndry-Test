# -*- coding: utf-8 -*-
""""""
"""
Created on Tue Dec 28 19:03:40 2021

@author: Nicolas Striebig
"""

import re
import math
import binascii

import logging
from modules.setup_logger import logger


logger = logging.getLogger(__name__)

class Decode:

    def find_idle_bytes_pos(self, readout: bytearray,
        start_seq: bytearray = b'\xaf(\x2f*)',
        idle_seq: bytearray = b'(\x2f{1,})[\0-\x0F]') -> list:
        """
            Find idle Bytes

        :param readout: Readout streeam
        :param start_seq: Start sequence regex
        :param idle_seq: Idle sequence regex

        :returns: Tuples with idle byte strings start and stop pos
        """
        matches = []

        # Look for start seq
        start = re.search(start_seq,readout)
        if start is not None:
            matches.append((start.start(), start.end()-1))

        # Find idle seqs and append to list
        for index, match in enumerate(re.finditer(idle_seq,readout)):
            match_start = match.start()
            match_end = match.end()-1

            # print(f"Index: {index} Idle: {match_start} to {match_end}")

            if len(matches) > 0:
                # print(f"Prev match end:{matches[index][1]}")
                match_start = matches[index][1] + math.ceil((match_start - matches[index][1])/5)*5

            matches.append((match_start, match_end))
            # print(f"Index: {index} Idle: {match_start} to {match_end}")

        # remove probably redundant first match
        if matches[0][1] == matches[1][1]:
            del matches[1]

        logger.info(f"Matches: {matches}")
        return matches

    def hits_from_readoutstream(self, readout: bytearray) -> list:
        """
        Extract Hits from Readout stream

        :param readout: Readout streeam

        :returns: List of hits
        """

        matches = self.find_idle_bytes_pos(readout)

        # print(f"Matches: {matches}")

        count = 0

        list_hits = []

        if len(matches) > 1: # if no hits, there is one tuple (0:end)
            for index, match in enumerate(matches[:-1]): #exclude last item
                logger.info(f"Hit: {binascii.hexlify(readout[match[1]:(match[1]+5)])}")
                match2 = 5 + match[1]

                list_hits.append(readout[match[1]:(match[1]+5)])

                count += 1

                # print(f"Index: {index} len(matches): {len(matches)}")
                if index < len(matches)-1:
                    while matches[index+1][0] > match2: # and matches[index+1][1] < len(readout):
                        logger.info(f"Hit: {binascii.hexlify(readout[match2:(match2+5)])} Match: {match2} next: {matches[index+1]}")
                        list_hits.append(readout[match2:(match2+5)])
                        match2 += 5
                        count += 1

        logger.info(f"Number of Hits {count}")
        logger.debug(f" Hitlist: {list_hits}")

        return list_hits


    def decode_hits(self):
        pass

