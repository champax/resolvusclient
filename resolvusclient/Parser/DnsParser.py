"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2018 Laurent Labatut / Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""
import logging

from dnslib import DNSRecord
from pysolbase.SolBase import SolBase

logger = logging.getLogger(__name__)


class DnsParser(object):
    """
    Dns parser.
    Doc : https://justanapplication.wordpress.com/category/dns/dns-messages/dns-message-format/dns-message-header-format/
    Doc : https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
    """

    @classmethod
    def try_parse_dns(cls, prev_buffer, bin_buffer):
        """
        Try parse a dns buffer.
        Do not handle several dns buffer coming over the same socket since header do not have a simple binary length field.
        :param prev_buffer: Previous (incomplete) buffer.
        :type prev_buffer: bytes,None
        :param bin_buffer: Incoming received buffer.
        :type bin_buffer: bytes
        :return tuple DNSRecord|None, incomplete_buffer|None
        :rtype tuple
        """

        # Accu
        if not prev_buffer:
            cur_buffer = bin_buffer
        else:
            cur_buffer = prev_buffer + bin_buffer

        # Try it
        try:
            dns_record = DNSRecord.parse(cur_buffer)
            return dns_record, None
        except Exception as e:
            logger.info("Parse failed, ex=%s", SolBase.extostr(e))
            return None, cur_buffer
