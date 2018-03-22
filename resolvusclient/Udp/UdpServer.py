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
from dnslib import DNSRecord
from gevent.server import DatagramServer
from pysolbase.SolBase import SolBase
from pysolmeters.Meters import Meters
from pysoltcp.tcpbase.TcpSocketManager import TcpSocketManager

logger = logging.getLogger(__name__)


class UdpServer(DatagramServer):
    """
    Udp server
    """

    UDP_SOCKET_HOST = "0.0.0.0"
    UDP_SOCKET_PORT = 53

    UDP_UNITTEST_SOCKET_HOST = "0.0.0.0"
    UDP_UNITTEST_SOCKET_PORT = 63053

    DEFAULT_RESOLVERS = ["8.8.8.8"]

    def __init__(self,
                 listen_host=None, listen_port=None,
                 ar_resolvers=None,
                 resolve_timeout_ms=10000,
                 ut_incoming_callback=None, ut_outgoing_callback=None, *args, **kwargs):
        """
        Init
        :param listen_host: str,None
        :type listen_host: str,None
        :param listen_port: int,None
        :type listen_port: int,None
        :param ar_resolvers: List of resolver hosts
        :type ar_resolvers: list,None
        :param ut_incoming_callback: callable,None. UNITTEST ONLY.
        :type ut_incoming_callback: callable,None
        :param ut_outgoing_callback: callable,None. UNITTEST ONLY.
        :type ut_outgoing_callback: callable,None
        """

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

        # Resolvers
        self.ar_resolvers = ar_resolvers
        if not self.ar_resolvers:
            self.ar_resolvers = UdpServer.DEFAULT_RESOLVERS

        # Store
        self.resolve_timeout_ms = resolve_timeout_ms
        self.ut_incoming_callback = ut_incoming_callback
        self.ut_outgoing_callback = ut_outgoing_callback

        # Log
        logger.info("Using listen_host=%s, listen_port=%s", self.listen_host, self.listen_port)
        logger.info("Using ar_resolvers=%s", ar_resolvers)
        logger.info("Using resolve_timeout_ms=%s", resolve_timeout_ms)
        logger.info("Using ut_incoming_callback=%s", self.ut_incoming_callback)
        logger.info("Using ut_outgoing_callback=%s", self.ut_outgoing_callback)

        # Init
        self._is_started = False
        self._server_greenlet = None
        self._soc = None

        # Allocate socket and bind it
        self._create_socket_and_bind()

        # Call base
        logger.info("Calling base")
        DatagramServer.__init__(self, self._soc, *args, **kwargs)

    def start(self):
        """
        Start (async)
        """

        if self._is_started:
            logger.warning("Already started, bypass")
            return

        # Base start
        logger.info("Starting (spawn start)")

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
        logger.info("Closing socket")
        TcpSocketManager.safe_close_socket(self._soc)

        # Signal stopped
        logger.info("Stopped")
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
        Handle one udp message.
        This is called via spawn, so we are free to be slow.
        :param data: data
        :type data: bytes
        :param address: address
        :type address: str
        """

        ms_start = SolBase.mscurrent()
        try:
            logger.info("Incoming, address=%s, data=%s", address, repr(data))
            # Handle data
            self._handle_udp(data)

            # Stats
            Meters.aii("resolvusclient_udp_recv")
        except Exception as e:
            # Log
            logger.warning("Handle failed, data_len=%s, address=%s, data=%s, ex=%s", len(data), repr(address), repr(data), SolBase.extostr(e))

            # Stat
            Meters.aii("resolvusclient_udp_recv_ex")
        finally:
            Meters.dtci("resolvusclient_udp_recv_dtc", SolBase.msdiff(ms_start))

    # ------------------------------
    # UDP HANDLING
    # ------------------------------

    def _handle_udp(self, data):
        """
        Handle one udp message
        :param data: data
        :type data: bytes
        """

        # Log
        logger.info("Processing, data=%s", repr(data))

        # Unittest
        if self.ut_incoming_callback:
            b = self.ut_incoming_callback(data)
            if b:
                # Unittest has requested processing stop
                return

        # Parse
        question_dns = DNSRecord.parse(data)
        logger.info("Got question_dns=%s", repr(question_dns))

        # Query
        ms = SolBase.mscurrent()
        response_bin = question_dns.send(
            dest=self.ar_resolvers[0],
            port=53,
            tcp=False,
            timeout=self.resolve_timeout_ms/1000.0,
            ipv6=False,
        )
        logger.info("Got ms=%.2f, response_bin=%s", SolBase.msdiff(ms), repr(response_bin))

        # Parse it
        response_dns = DNSRecord.parse(response_bin)
        logger.info("Got response_dns=%s", repr(response_dns))

        # Unittest
        if self.ut_outgoing_callback:
            self.ut_outgoing_callback(response_bin)





