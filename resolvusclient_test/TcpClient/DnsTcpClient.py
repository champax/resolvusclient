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
# noinspection PyProtectedMember
from gevent.queue import Empty
from pysolbase.SolBase import SolBase
from pysolmeters.Meters import Meters
from random import randint

from pysoltcp.tcpclient.TcpSimpleClient import TcpSimpleClient

from resolvusclient.Parser.DnsParser import DnsParser

SolBase.logging_init()
logger = logging.getLogger(__name__)


class DnsTcpClient(TcpSimpleClient):
    """
    Dns tcp simple client
    """

    def __init__(self, tcp_client_config):
        """
        Constructor.
        :param tcp_client_config: Tcp client configuration.
        """

        # Base call
        TcpSimpleClient.__init__(self, tcp_client_config)

        # Server PID
        self._server_pid = None

        # Instance protocol lock
        self._protocol_lock = RLock()

        # Incomplete
        self.incomplete_buffer = None

        # Answer list
        self.ar_answer = list()

    # =================================
    # CONNECT
    # =================================

    def connect(self):
        """
        Connect to server.
        :return Return true upon success.
        """

        # Stats
        Meters.aii("dnstcp.client.client_connect_count")

        # Call base
        dt_start = SolBase.datecurrent()
        b = TcpSimpleClient.connect(self)
        if not b:
            # Stat
            logger.error("connect failed, fatal, exiting")
            Meters.aii("dnstcp.client.client_connect_error")

            # Exit
            return False

        # Stat
        Meters.dtci("dnstcp.client.delay_client_connect", SolBase.datediff(dt_start))

        return True

    # =================================
    # DISCONNECT
    # =================================

    def disconnect(self):
        """
        Disconnect from server.
        :return Return true upon success.
        """

        # Stat
        Meters.aii("dnstcp.client.client_disconnect_count")

        # Base
        return TcpSimpleClient.disconnect(self)

    # =================================
    # RECEIVE
    # =================================

    def _on_receive(self, binary_buffer):
        """
        Callback called upon server receive.
        :param binary_buffer: The binary buffer received.
        :type binary_buffer: bytes
        """

        # Received something...
        logger.debug("binary_buffer=%s", binary_buffer)

        # We do not call base (no need of queueing stuff)
        # Direct parsing : answer
        answer_dns, self.incomplete_buffer = DnsParser.try_parse_dns(self.incomplete_buffer, binary_buffer)
        logger.info("Got answer_dns=%s", repr(answer_dns))
        if answer_dns is None:
            assert self.incomplete_buffer is not None, "answer_dns None, need incomplete_buffer"
            # Cannot process now
            return
        else:
            assert self.incomplete_buffer is None, "answer_dns set, need incomplete_buffer None"

        # In queue
        self.ar_answer.append(answer_dns)

        # And its over for us
        self.disconnect()




