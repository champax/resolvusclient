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
from threading import RLock

import gevent
from pysolbase.SolBase import SolBase
from pysolmeters.Meters import Meters
from pysoltcp.tcpbase.SignaledBuffer import SignaledBuffer
from pysoltcp.tcpserver.clientcontext.TcpServerClientContext import TcpServerClientContext

from resolvusclient.Parser.DnsParser import DnsParser

SolBase.logging_init()
logger = logging.getLogger(__name__)


class TcpServerContext(TcpServerClientContext):
    """
    Tcp server client context.
    """

    def __init__(self, tcp_server, client_id, client_socket, client_addr):
        """
        Constructor.
        :param tcp_server: The tcp server.
        :param client_id: The client id.
        :param client_socket: The client socket.
        :param client_addr: The client address.

        """

        # Base - we provide two callback :
        # - one for disconnecting ourselves
        # - one to notify socket receive buffer
        TcpServerClientContext.__init__(self, tcp_server, client_id, client_socket, client_addr)

        # Intervals (will be set by the factory)
        self._helloTimeOutMs = 0

        # Greenlets
        self._helloTimeOutGreenlet = None

        # Instance protocol lock
        self._protocolLock = RLock()

        # Timestamp
        self.dtClientConnect = None

        # Stop calls
        self.stop_synch_internalCalled = False
        self.stop_synchCalled = False

        # Resolve stuff
        self.ar_resolvers = None
        self.resolve_timeout_ms = None

        # Incomplete binary buffer
        self.incomplete_buffer = None

    # =================================
    # CONNECT
    # =================================

    def start(self):
        """
        Start.
        :return Return true upon success.
        """

        # Timestamp
        self.dtClientConnect = SolBase.datecurrent()

        # Call base
        b = TcpServerClientContext.start(self)
        if not b:
            # Stat
            logger.error("start failed, fatal, exiting")
            Meters.aii("dnstcp.server.serverStartError")

            # Exit
            return False

        # Stat
        Meters.aii("dnstcp.server.serverStartCount")

        # Ok
        return True

    # =================================
    # DISCONNECT
    # =================================

    def stop_synch_internal(self):
        """
        Disconnect from server.
        :return Return true upon success.
        """

        # Stat
        Meters.aii("dnstcp.server.serverStopSynchCount")

        # Called
        self.stop_synch_internalCalled = True

        # Base
        return TcpServerClientContext.stop_synch_internal(self)

    def stop_synch(self):
        """
        Stop synch
        """

        # Called
        self.stop_synchCalled = True

        # Base
        return TcpServerClientContext.stop_synch(self)

    # =================================
    # RECEIVE
    # =================================

    def _on_receive(self, binary_buffer):
        """
        Callback called upon server receive.
        :param binary_buffer: Received buffer.

        """

        # Received something...
        logger.debug("binary_buffer=%s", binary_buffer)

        # Parse question
        question_dns, self.incomplete_buffer = DnsParser.try_parse_dns(self.incomplete_buffer, binary_buffer)
        logger.info("Got question_dns=%s", repr(question_dns))
        if question_dns is None:
            assert self.incomplete_buffer is not None, "question_dns None, need incomplete_buffer"
            # Cannot process now
            return
        else:
            assert self.incomplete_buffer is None, "question_dns set, need incomplete_buffer None"

        # Query
        ms = SolBase.mscurrent()
        response_bin = question_dns.send(
            dest=self.ar_resolvers[0],
            port=53,
            tcp=False,
            timeout=self.resolve_timeout_ms / 1000.0,
            ipv6=False,
        )
        logger.info("Got ms=%.2f, response_bin=%s", SolBase.msdiff(ms), repr(response_bin))

        # Parse it
        response_dns, incomplete_buffer = DnsParser.try_parse_dns(None, response_bin)
        logger.info("Got response_dns=%s", repr(response_dns))
        assert response_dns, "Need response_dns, got None"
        assert incomplete_buffer is None, "Need full parsing"

        # Send back and wait (we are covered by tcp server absolute / relative timeouts)
        sb = SignaledBuffer()
        sb.binary_buffer = response_bin
        self.send_binary_to_socket_with_signal(sb)
        sb.send_event.wait()

        # Close us async (this is over for us, send is signaled, tcp here is open/req/resp/close).
        self.stop_asynch()
