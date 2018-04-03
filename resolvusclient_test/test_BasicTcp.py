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
from pysolbase.SolBase import SolBase
from pysoltcp.tcpserver.TcpServer import TcpServer
from pysoltcp.tcpserver.TcpServerConfig import TcpServerConfig

from resolvusclient.Tcp.TcpServerContextFactory import TcpServerContextFactory

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
        server_config.listen_port = 3201
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

    def test_start_stop_loop_10(self):
        """
        Test
        """

        for i in range(0, 10):
            # Start
            self._start_server_and_check()

            # Stop
            self._stop_server_and_check()
