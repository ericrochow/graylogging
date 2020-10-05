#!/usr/bin/env python3

import json
import logging
import socket

from graylogging.tools import validate_gelf_payload


class TCPGELF(object):
    def __init__(self, host, port, debug=False):
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

    def push_log(self, payload: dict):
        """
        Sends a message to Graylog using GELF over TCP.

        Args:
          payload: A dict containing the log message and metadata to push to Graylog
        Returns:
          None
        Raises:
          OSError: Unable to create or use a TCP socket.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            log = json.dumps(payload).encode("gbk")
            try:
                s.sendall(log + b"\0")
            except OSError:
                self.logger.exception(
                    "Failed to send the following log entry: %s", log
                )
                pass
            s.shutdown(1)

    def send_gelf(self, payload: dict):
        """"""
        if validate_gelf_payload(payload):
            return self.push_log(payload)
