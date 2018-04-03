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
import unittest

import os
from dnslib import DNSRecord
from pysolbase.SolBase import SolBase
from pysoltcp.tcpclient.TcpClientConfig import TcpClientConfig
from pysoltcp.tcpserver.TcpServer import TcpServer
from pysoltcp.tcpserver.TcpServerConfig import TcpServerConfig

from resolvusclient.Tcp.TcpServerContextFactory import TcpServerContextFactory
from resolvusclient.Udp.UdpServer import UdpServer
from resolvusclient_test.TcpClient.DnsTcpClient import DnsTcpClient

SolBase.voodoo_init()
logger = logging.getLogger(__name__)


class TestBasicTcp(unittest.TestCase):
    """
    Test description
    """

    def setUp(self):
        """
        Setup (called before each test)
        """

        os.environ.setdefault("KNOCK_UNITTEST", "yes")
        self.tcp_server = None

    def tearDown(self):
        """
        Setup (called after each test)
        """
        if self.tcp_server:
            self._stop_server_and_check()

    def _start_server_and_check(self):
        """
        Test
        """
        # Config
        server_config = TcpServerConfig()
        server_config.listen_addr = "127.0.0.1"
        server_config.listen_port = UdpServer.UDP_UNITTEST_SOCKET_PORT
        server_config.client_factory = TcpServerContextFactory()
        server_config.socket_absolute_timeout_ms = 60000
        server_config.socket_relative_timeout_ms = 60000

        # Allocate
        self.tcp_server = TcpServer(server_config)

        # Check
        self.assertIsNotNone(self.tcp_server)
        self.assertFalse(self.tcp_server._is_started)
        self.assertTrue(self.tcp_server._server is None)

        # Start
        self.assertTrue(self.tcp_server.start_server())
        self.assertTrue(self.tcp_server._is_started)
        self.assertFalse(self.tcp_server._server is None)

    def _stop_server_and_check(self):
        """
        Test

        """
        # Stop
        self.tcp_server.stop_server()
        self.assertFalse(self.tcp_server._is_started)
        self.assertTrue(self.tcp_server._server is None)

        # Reset
        self.tcp_server = None

    def test_start_resolve_stop_loop_10(self):
        """
        Test
        """

        for i in range(0, 10):
            # Start
            self._start_server_and_check()

            # Connect tcp
            client_config = TcpClientConfig()
            client_config.target_addr = "127.0.0.1"
            client_config.target_port = UdpServer.UDP_UNITTEST_SOCKET_PORT
            tcp_client = DnsTcpClient(client_config)
            self.assertTrue(tcp_client.connect())
            self.assertTrue(tcp_client.is_connected)

            # Send basic resolving
            question_dns = DNSRecord.question("knock.center")
            logger.info("question_dns=%s", repr(question_dns))
            question_bin = question_dns.pack()
            logger.info("question_bin=%s", question_bin)
            tcp_client.send_binary_to_socket(question_bin)

            # Wait for processing
            ms = SolBase.mscurrent()
            while SolBase.msdiff(ms) < 20000:
                # Check
                if len(tcp_client.ar_answer) > 0 and tcp_client.is_connected == False:
                    break
                else:
                    SolBase.sleep(500)
                    logger.info("Waiting len=%s, connected=%s", tcp_client.ar_answer, tcp_client.is_connected)

            # Check it
            self.assertEqual(len(tcp_client.ar_answer), 1)
            self.assertFalse(tcp_client.is_connected)

            # Stop
            self._stop_server_and_check()
