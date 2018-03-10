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
from resolvusclient.Platform.PlatformTools import PlatformTools

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class UdpServer(DatagramServer):
    """
    Udp server
    """

    # --------------------------
    # UNIX DOMAIN SOCKET
    # --------------------------
    UDP_SOCKET_NAME = "/var/run/resolvusclient.udp.socket"
    UDP_UNITTEST_SOCKET_NAME = "/tmp/resolvusclient.udp.socket"

    # --------------------------
    # WINDOWS SOCKET (WINDOWS ONLY)
    # --------------------------
    UDP_WINDOWS_SOCKET_HOST = "localhost"
    UDP_WINDOWS_SOCKET_PORT = "63184"

    UDP_WINDOWS_UNITTEST_SOCKET_HOST = "localhost"
    UDP_WINDOWS_UNITTEST_SOCKET_PORT = "63999"

    def __init__(self, socket_name=None, windows_host=None, windows_port=None, *args, **kwargs):
        """
        Init
        :param socket_name: str,None
        :type socket_name: str,None
        :param windows_host: str,None
        :type windows_host: str,None
        :param windows_port: int,None
        :type windows_port: int,None
        """

        # Call base
        DatagramServer.__init__(self, *args, **kwargs)

        # NAME
        if socket_name:
            self._socket_name = socket_name
        else:
            # If UNITTEST, force
            if "KNOCK_UNITTEST" in os.environ:
                self._socket_name = UdpServer.UDP_UNITTEST_SOCKET_NAME
            else:
                self._socket_name = UdpServer.UDP_SOCKET_NAME

        # WINDOWS HOST
        if windows_host:
            self._windows_host = windows_host
        else:
            # If UNITTEST, force
            if "KNOCK_UNITTEST" in os.environ:
                self._windows_host = UdpServer.UDP_WINDOWS_UNITTEST_SOCKET_HOST
            else:
                self._windows_host = UdpServer.UDP_WINDOWS_SOCKET_HOST

        # WINDOWS PORT
        if windows_port:
            self._windows_port = windows_port
        else:
            # If UNITTEST, force
            if "KNOCK_UNITTEST" in os.environ:
                self._windows_port = UdpServer.UDP_WINDOWS_UNITTEST_SOCKET_PORT
            else:
                self._windows_port = UdpServer.UDP_WINDOWS_SOCKET_PORT

        # Init
        self._is_started = False
        self._server_greenlet = None

        # Logs
        logger.info("_socket_name=%s", self._socket_name)
        logger.info("_windows_host=%s", self._windows_host)
        logger.info("_windows_port=%s", self._windows_port)

    def start(self):
        """
        Start (async)
        """

        if self._is_started:
            logger.warn("Already started, bypass")
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
            logger.warn("Not started, bypass")
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

        # Remove socket
        try:
            if os.path.exists(self._socket_name):
                os.remove(self._socket_name)
        except Exception as e:
            logger.warn("Socket file remove ex=%s", SolBase.extostr(e))

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
        logger.info("Binding")

        # Alloc
        if PlatformTools.get_distribution_type() == "windows":
            # ==========================
            # Ahah, no support for domain socket on Windows
            # ==========================
            # Will not go for pipes
            # So we target local host (dirty)
            logger.warn("Windows detected, using UDP toward %s:%s (lacks of domain socket support)", self._windows_host, self._windows_port)
            logger.warn("You may (will) experience performance issues over the UDP channel (possible lost of packets)")
            logger.warn("If you are using client library, please be sure to NOT target the unix domain socket on this machine.")
            self._soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Switch to non blocking
            self._soc.setblocking(0)

            # Bind
            self._soc.bind((self._windows_host, self._windows_port))
        else:
            # ==========================
            # Linux rocks (and debian rocks more)
            # ==========================

            # Alloc
            self._soc = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            if os.path.exists(self._socket_name):
                os.remove(self._socket_name)

            # Switch to non blocking
            self._soc.setblocking(0)

            # Bind
            self._soc.bind(self._socket_name)

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
