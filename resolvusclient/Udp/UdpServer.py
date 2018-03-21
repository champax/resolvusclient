"""
-*- coding: utf-8 -*-
===============================================================================

Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac



 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
 ===============================================================================
"""
import logging
import socket

import gevent
import os
from gevent.server import DatagramServer
from pysolbase.SolBase import SolBase
from pysolmeters.Meters import Meters

from resolvusclient.Helpers.SocketHelpers import SocketHelpers

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class UdpServer(DatagramServer):
    """
    Udp server
    """

    UDP_SOCKET_HOST = "localhost"
    UDP_SOCKET_PORT = "53"

    UDP_UNITTEST_SOCKET_HOST = "localhost"
    UDP_UNITTEST_SOCKET_PORT = "63053"

    def __init__(self, listen_host=None, listen_port=None, *args, **kwargs):
        """
        Init
        :param listen_host: str,None
        :type listen_host: str,None
        :param listen_port: int,None
        :type listen_port: int,None
        """

        # Call base
        DatagramServer.__init__(self, *args, **kwargs)

        # UNITTEST
        if "KNOCK_UNITTEST" in os.environ:
            self.listen_host = UdpServer.UDP_UNITTEST_SOCKET_HOST
            self.listen_port = UdpServer.UDP_UNITTEST_SOCKET_PORT
        else:
            self.listen_host = listen_host
            self.listen_port = listen_port

        # Default
        if not self.listen_host:
            self.listen_host = UdpServer.UDP_SOCKET_HOST
        if not self.listen_port:
            self.listen_port = UdpServer.UDP_SOCKET_PORT

        # Log
        logger.info("Using listen_host=%s, listen_port=%s", self.listen_host, self.listen_port)

        # Init
        self._is_started = False
        self._server_greenlet = None

    def start(self):
        """
        Start (async)
        """

        if self._is_started:
            logger.warning("Already started, bypass")
            return

            # Base start
        logger.info("Starting")

        # Spawn async toward base
        self._server_greenlet = gevent.spawn(DatagramServer.start, self)
        logger.info("Started")

        # Signal started
        self._is_started = True

    def stop(self, timeout=None):
        """
        Stop
        """

        if not self._is_started:
            logger.warning("Not started, bypass")
            return

        # Base stop
        logger.info("Stopping base")
        DatagramServer.stop(self, timeout=timeout)
        logger.info("Stopped base")

        # Greenlet stop
        if self._server_greenlet:
            logger.info("Killing _server_greenlet")
            self._server_greenlet.kill()
            self._server_greenlet = None

        # Close socket
        SocketHelpers.safe_close_socket(self._soc)

        # Signal stopped
        self._is_started = False

    def _create_socket_and_bind(self):
        """
        Create socket
        """

        if self._soc:
            logger.info("Bypass, _soc set")
            return

        # Listen
        logger.info("Binding on %s:%s", self.listen_host, self.listen_port)

        # Alloc
        self._soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Switch to non blocking
        self._soc.setblocking(0)

        # Bind
        self._soc.bind((self.listen_host, self.listen_port))

        # Logs
        logger.info("Recv buf=%s", self._soc.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
        logger.info("Send buf=%s", self._soc.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))

        # Increase recv
        try:
            self._soc.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 1024)
        except Exception as e:
            logger.info("SO_RCVBUF increased failed, ex=%s", SolBase.extostr(e))

        # Logs
        logger.info("Recv buf=%s", self._soc.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
        logger.info("Send buf=%s", self._soc.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))

    # ------------------------------
    # HANDLE INCOMING STUFF
    # ------------------------------

    def handle(self, data, address):
        """
        Handle one udp message
        :param data: data
        :type data: str
        :param address: address
        :type address: str
        """

        ms_start = SolBase.mscurrent()
        try:
            # Handle data
            pass

            # Stats
            Meters.aii("resolvusclient_udp_recv")
        except Exception as e:
            # Log
            logger.warning("Handle failed, data_len=%s, address=%s, data=%s, ex=%s", len(data), repr(address), repr(data), SolBase.extostr(e))

            # Stat
            Meters.aii("resolvusclient_udp_recv_ex")
        finally:
            Meters.dtci("resolvusclient_udp_recv_dtc", SolBase.msdiff(ms_start))
