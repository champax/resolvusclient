"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
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
import socket
import unittest

import os
from dnslib import DNSRecord
from pysolbase.SolBase import SolBase
from pysoltcp.tcpbase.TcpSocketManager import TcpSocketManager

from resolvusclient.Udp.UdpServer import UdpServer

SolBase.voodoo_init()
logger = logging.getLogger(__name__)


class TestBasicUdp(unittest.TestCase):
    """
    Test description
    """

    def setUp(self):
        """
        Setup (called before each test)
        """

        os.environ.setdefault("KNOCK_UNITTEST", "yes")
        self.udp_server = None

        # Receive udp and boolean to return (if True : stop processing)
        self.ar_udp_in = list()
        self.ar_udp_out = list()
        self.udp_callback_stop_processing = True

    def tearDown(self):
        """
        Setup (called after each test)
        """
        if self.udp_server:
            self._stop_server()

    def _start_server(self):
        """
        Test
        """

        # Check
        self.assertIsNone(self.udp_server)

        # Alloc
        self.udp_server = UdpServer(
            ut_incoming_callback=self._udp_incoming_callback,
            ut_outgoing_callback=self._udp_outgoing_callback,

        )

        # Start
        self.udp_server.start()

        # Check
        self.assertTrue(self.udp_server._is_started)

    def _stop_server(self):
        """
        Test
        """

        # Check
        self.assertIsNotNone(self.udp_server)

        # Stop
        self.udp_server.stop()

        # Check
        self.assertFalse(self.udp_server._is_started)

        # Reset
        self.udp_server = None

    def _udp_incoming_callback(self, data):
        """
        Callback
        :param data: bytes
        :type data: bytes
        :return True if processing is stopped by us
        :rtype bool
        """

        if self.ar_udp_in is not None:
            logger.info("callback (adding), data=%s", repr(data))
            self.ar_udp_in.append(data)
        else:
            logger.warning("callback (none), data=%s", repr(data))
        return self.udp_callback_stop_processing

    def _udp_outgoing_callback(self, data):
        """
        Callback
        :param data: bytes
        :type data: bytes
        :return True if processing is stopped by us
        :rtype bool
        """

        if self.ar_udp_out is not None:
            logger.info("callback (adding), data=%s", repr(data))
            self.ar_udp_out.append(data)
        else:
            logger.warning("callback (none), data=%s", repr(data))

    @classmethod
    def _client_send(cls, buf):
        """
        Client udp send
        :param buf: bytes
        :type buf: bytes
        """

        soc = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
        soc.connect((UdpServer.UDP_UNITTEST_SOCKET_HOST, UdpServer.UDP_UNITTEST_SOCKET_PORT))
        SolBase.sleep(0)
        soc.sendall(buf)
        SolBase.sleep(0)
        TcpSocketManager.safe_close_socket(soc)
        SolBase.sleep(0)

    def test_start_stop_loop_10(self):
        """
        Test
        """

        timeout_ms = 5000

        for i in range(0, 10):
            # Start
            self._start_server()

            # Send
            for j in range(0, 10):
                # Reset
                self.ar_udp_in = list()

                # Send
                buf = "UDP_%s_%s" % (i, j)
                bin_buf = SolBase.unicode_to_binary(buf)
                self._client_send(bin_buf)

                # Wait for processing
                ms = SolBase.mscurrent()
                while SolBase.msdiff(ms) < timeout_ms:
                    # Check
                    if len(self.ar_udp_in) > 0:
                        break
                    else:
                        SolBase.sleep(0)

                # Check it
                self.assertEqual(len(self.ar_udp_in), 1)
                self.assertEqual(self.ar_udp_in[0], bin_buf)

            # Stop
            self._stop_server()

    def test_simple_resolving(self):
        """
        Test
        """

        # Process
        self.udp_callback_stop_processing = False

        # Start
        self._start_server()

        # Send basic resolving
        question_dns = DNSRecord.question("knock.center")
        logger.info("question_dns=%s", repr(question_dns))
        question_bin = question_dns.pack()
        logger.info("question_bin=%s", question_bin)
        self._client_send(question_bin)

        # Wait for processing
        ms = SolBase.mscurrent()
        while SolBase.msdiff(ms) < 20000:
            # Check
            if len(self.ar_udp_in) > 0 and len(self.ar_udp_out):
                break
            else:
                SolBase.sleep(500)
                logger.info("Waiting len in/out=%s/%s", len(self.ar_udp_in), len(self.ar_udp_out))

        # Check it
        self.assertEqual(len(self.ar_udp_in), 1)
        self.assertEqual(self.ar_udp_in[0], question_bin)
        self.assertEqual(len(self.ar_udp_out), 1)

        # Stop
        self._stop_server()