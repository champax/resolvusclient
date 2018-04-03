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

# Logger
import logging

from pysolbase.SolBase import SolBase
from pysoltcp.tcpserver.basefactory.TcpServerClientContextAbstractFactory import TcpServerClientContextAbstractFactory

from resolvusclient.Tcp.TcpServerContext import TcpServerContext
from resolvusclient.Udp.UdpServer import UdpServer

SolBase.logging_init()
logger = logging.getLogger(__name__)


class TcpServerContextFactory(TcpServerClientContextAbstractFactory):
    """
    Default factory.
    """

    def __init__(self, hello_timeout_ms=10000, ar_resolvers=None, resolve_timeout_ms=10000):
        """
        Constructor.
        :param ar_resolvers: List of resolver hosts
        :type ar_resolvers: list,None
        :param hello_timeout_ms: Timeout in millis.
        :type hello_timeout_ms: int
        """

        # Timeout
        self._hello_timeout_ms = hello_timeout_ms

        # Resolvers
        self.resolve_timeout_ms = resolve_timeout_ms
        self.ar_resolvers = ar_resolvers
        if not self.ar_resolvers:
            self.ar_resolvers = UdpServer.DEFAULT_RESOLVERS

        logger.info("_hello_timeout_ms=%s, type=%s", self._hello_timeout_ms, SolBase.get_classname(self._hello_timeout_ms))

    def get_new_clientcontext(self, tcp_server, client_id, client_socket, client_addr):
        """
        Return a new client context instance.
        :param tcp_server: The tcpserver instance.
        :param client_id: an integer, which is the unique id of this client.
        :param client_socket: The server socket.
        :param client_addr: The remote addr information.
        :return Returned object MUST be a subclass of TcpServerClientContext.
        """
        new_client = TcpServerContext(tcp_server, client_id, client_socket, client_addr)
        new_client._helloTimeOutMs = self._hello_timeout_ms
        new_client.ar_resolvers = self.ar_resolvers
        new_client.resolve_timeout_ms = self.resolve_timeout_ms
        return new_client
