#!/usr/bin/env python3

import json
import logging
import socket

from graylogging.tools import validate_gelf_payload


class UDPGELF(object):
    def __init__(self, host, port, debug=False):
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

    def push_logs(self, payload: dict):
        """

        Args:
          payload: A dict containing the log and metadata to push to Graylog
        Returns:
          None
        Raises:
          OSError: Failed to send log over the UDP socket
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            log = json.dumps(payload).encode("gbk")
            try:
                s.sendto(log, (self.host, self.port))
            except OSError:
                self.logger.exception(
                    "Failed to send the following log entry: %s", log
                )

    def send_gelf(self, payload: dict):
        """"""
        if validate_gelf_payload(payload):
            return self.push_logs(payload)
