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

from pysolbase.SolBase import SolBase

logger = logging.getLogger(__name__)


class SocketHelpers(object):
    """
    Socket helpers
    """

    @classmethod
    def safe_close_socket(cls, soc_to_close):
        """
        Safe close a socket
        :param cls: cls
        :param soc_to_close: socket
        :return: Nothing
        """

        if soc_to_close is None:
            return

        try:
            soc_to_close.shutdown(2)
        except Exception as e:
            logger.debug("Socket shutdown ex=%s", SolBase.extostr(e))

        try:
            soc_to_close.close()
        except Exception as e:
            logger.debug("Socket close ex=%s", SolBase.extostr(e))

        try:
            del soc_to_close
        except Exception as e:
            logger.debug("Socket del ex=%s", SolBase.extostr(e))
