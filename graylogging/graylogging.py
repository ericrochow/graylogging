#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
import socket
import time
from typing import Optional, Union

from graylogging.http_client import HTTPGELF
from graylogging.tcp_client import TCPGELF
from graylogging.udp_client import UDPGELF


class GraylogFormatter(logging.Formatter):
    """"""

    def __init__(self):

        super(GraylogFormatter, self).__init__()

    @classmethod
    def format_record(
        cls,
        short_message: str,
        host: str = socket.gethostname(),
        full_message: str = None,
        version: str = "1.1",
        timestamp: str = None,
        level: int = 1,
        _appname: str = None,
        **kwargs,
    ) -> dict:
        """
        Formats input to a dict meeting the GELF specificaiton. Arbitrary
        fields may be added to the payload so long as they are prepended with
        an underscore (_).

        Args:
          host: A string containing the name of the host, source, or
              application that sent the log message
          short_message: A string containing a short, descriptive message
          full_message: A string containing detailed information such as
              backtraces (optional)
          version: A string specifying the GELF spec version. Should be '1.1'
          timestamp: A string specifying the time of the log entry (optional,
              defaults to current time)
          level: An integer specifying the syslog level or the associated
              string name of that level (optional, defaults to 1/ALERT)
              the log message
          _appname: A string containing the name of the application logging
        Returns:
          A GELF-formatted dictionary formatted to POST to the graylog server.
        """
        payload = {
            "version": version,
            "host": host,
            "short_message": short_message,
            "level": GraylogHandler.encodeLogLevel(level),
            "timestamp": GraylogHandler._get_timestamp(timestamp),
            "_application": _appname,
        }
        if full_message:
            payload["full_message"] = full_message
        extra_args = GraylogHandler._extra_args(**kwargs)
        payload = {**payload, **extra_args}
        return payload


class GraylogHandler(logging.Handler):
    """
    A handler class which writes logging records, in GELF format, to a Graylog
    server.

    A handler class which writes logging records, in pickle format, to
    a streaming socket. The socket is kept open across logging calls.
    If the peer resets it, an attempt is made to reconnect on the next call.
    The pickle which is sent is that of the LogRecord's attribute dictionary
    (__dict__), so that the receiver does not need to have the logging module
    installed in order to process the logging event.
    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.
    """

    # from <linux/sys/syslog.h>:
    # ======================================================================
    # priorities/facilities are encoded into a single 32-bit quantity, where
    # the bottom 3 bits are the priority (0-7) and the top 28 bits are the
    # facility (0-big number). Both the priorities and the facilities map
    # roughly one-to-one to strings in the syslogd(8) source code.  This
    # mapping is included in this file.
    #
    # priorities (these are ordered)

    LOG_EMERG = 0  # system is unusable
    LOG_ALERT = 1  # action must be taken immediately
    LOG_CRIT = 2  # critical conditions
    LOG_ERR = 3  # error conditions
    LOG_WARNING = 4  # warning conditions
    LOG_NOTICE = 5  # normal but significant condition
    LOG_INFO = 6  # informational
    LOG_DEBUG = 7  # debug-level messages

    #  facility codes
    LOG_KERN = 0  # kernel messages
    LOG_USER = 1  # random user-level messages
    LOG_MAIL = 2  # mail system
    LOG_DAEMON = 3  # system daemons
    LOG_AUTH = 4  # security/authorization messages
    LOG_SYSLOG = 5  # messages generated internally by syslogd
    LOG_LPR = 6  # line printer subsystem
    LOG_NEWS = 7  # network news subsystem
    LOG_UUCP = 8  # UUCP subsystem
    LOG_CRON = 9  # clock daemon
    LOG_AUTHPRIV = 10  # security/authorization messages (private)
    LOG_FTP = 11  # FTP daemon

    #  other codes through 15 reserved for system use
    LOG_LOCAL0 = 16  # reserved for local use
    LOG_LOCAL1 = 17  # reserved for local use
    LOG_LOCAL2 = 18  # reserved for local use
    LOG_LOCAL3 = 19  # reserved for local use
    LOG_LOCAL4 = 20  # reserved for local use
    LOG_LOCAL5 = 21  # reserved for local use
    LOG_LOCAL6 = 22  # reserved for local use
    LOG_LOCAL7 = 23  # reserved for local use

    level_names = [
        "EMERG",
        "ALERT",
        "CRITICAL",
        "ERROR",
        "WARNING",
        "NOTICE",
        "INFO",
        "DEBUG",
    ]

    priority_names = {
        "alert": LOG_ALERT,
        "crit": LOG_CRIT,
        "critical": LOG_CRIT,
        "debug": LOG_DEBUG,
        "emerg": LOG_EMERG,
        "err": LOG_ERR,
        "error": LOG_ERR,  # DEPRECATED
        "info": LOG_INFO,
        "notice": LOG_NOTICE,
        "panic": LOG_EMERG,  # DEPRECATED
        "warn": LOG_WARNING,  # DEPRECATED
        "warning": LOG_WARNING,
    }

    facility_names = {
        "auth": LOG_AUTH,
        "authpriv": LOG_AUTHPRIV,
        "cron": LOG_CRON,
        "daemon": LOG_DAEMON,
        "ftp": LOG_FTP,
        "kern": LOG_KERN,
        "lpr": LOG_LPR,
        "mail": LOG_MAIL,
        "news": LOG_NEWS,
        "security": LOG_AUTH,  # DEPRECATED
        "syslog": LOG_SYSLOG,
        "user": LOG_USER,
        "uucp": LOG_UUCP,
        "local0": LOG_LOCAL0,
        "local1": LOG_LOCAL1,
        "local2": LOG_LOCAL2,
        "local3": LOG_LOCAL3,
        "local4": LOG_LOCAL4,
        "local5": LOG_LOCAL5,
        "local6": LOG_LOCAL6,
        "local7": LOG_LOCAL7,
    }

    # The map below appears to be trivially lowercasing the key. However,
    # there's more to it than meets the eye - in some locales, lowercasing
    # gives unexpected results. See SF #1524081: in the Turkish locale,
    # "INFO".lower() != "info"
    priority_map = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warning",
        "ERROR": "error",
        "CRITICAL": "critical",
    }

    def __init__(
        self,
        host: str,
        port: int = None,
        transport: str = "tcp",
        facility: int = LOG_USER,
        hostname: str = socket.gethostname(),
        appname: str = None,
        verify: bool = True,
        close_on_error: bool = False,
    ) -> None:
        """
        Initialize a handler.

        Args:
          host: A string specifying the URL of the Graylog target
          port: An integer specifying the port number for the Graylog target
          facility: An integer specifying the log facility to use (optional,
              defaults to the value of LOG_USER: 1)
          appname: A string specifying the name of the application that is
              logging if different from `source` (optional)
          verify: A boolean specifying whether to verify the server's TLS cert
              (optional, defaults to True)
        Returns:
          An instantiated GraylogHandler object.
        """

        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        self.transport = transport
        self.facility = facility
        self.closeOnError = close_on_error
        self.hostname = hostname
        self.verify = verify
        if appname:
            self.appname = appname

    def _connect_graylog(self) -> Union[TCPGELF, UDPGELF, HTTPGELF]:
        """
        Instantiates a Graylog object.

        Args:
          None
        Returns:
          An instantiated Graylog object.
        Raises:
          ValueError: {self.transport} is not a valid transport type
        """
        if self.transport.lower() == "tcp":
            graylog = TCPGELF(self.host, self.port)
        elif self.transport.lower() == "udp":
            graylog = UDPGELF(self.host, self.port)
        elif self.transport.lower() == "http":
            graylog = HTTPGELF(self.host, self.port, timeout=10, verify=self.verify)
        else:
            raise ValueError(f"{self.transport} is not a valid transport type")
        return graylog

    @classmethod
    def _map_level_name(cls, level: str) -> str:
        """"""
        if level.upper() not in GraylogHandler.level_names:
            raise ValueError(
                f"{level} is not a valid log level. Please choose one of "
                f"{GraylogHandler.level_names}",
            )
        log_level = level.upper()
        return log_level

    @classmethod
    def _map_level_int_to_name(cls, level: int) -> str:
        """"""
        try:
            log_level = GraylogHandler.level_names[level]
        except IndexError:
            raise ValueError(
                f"{level} is not a valid log level. Expected values range from 0 to 7."
            )
        return log_level

    @staticmethod
    def _get_timestamp(timestamp: Union[float, str, None]) -> Union[float, str]:
        """
        Applies the timestamp if there isn't one already.

        Args:
          timestamp: A string containing the epoch-formatted timestamp or a
              None value
        Returns:
          A string containing the epoch-formatted timestamp.
        """
        if not timestamp:
            timestamp = time.time()
        return timestamp

    @staticmethod
    def _extra_args(**kwargs) -> dict:
        """
        Safely generates a dictionary of extra arguments to pass in the GELF
            payload.

        Args:
          kwargs:
        Returns:
          A dict containing the extra arguments.
        Raises:
          KeyError: Extra arguments must be prepended by `_` and must not be
              named `_id`
        """
        extra_args = {}
        if "_id" in kwargs:
            raise KeyError("'_id' is an internally used key and is not usable here")
        for key, value in kwargs.items():
            if key.startswith("_"):
                extra_args[key] = value
            else:
                raise KeyError(
                    "User-defined fields must be prepended with an underscore (_)."
                )
        return extra_args

    def send(self, payload: str) -> Optional[dict]:
        """
        Send a JSON object to the GELF endpoint.

        Args:
          payload: A JSON-formatted GELF payload
        Returns:
          The result of the POST to the GELF endpoint.
        """
        graylog = self._connect_graylog()
        return graylog.send_gelf(payload)

    def handleError(self, record) -> None:
        """
        Handle an error during logging.
        An error has occurred during logging. Most likely cause -
        connection lost. Close the session so that we can retry on the
        next event.

        Args:
          record: A record as provided by the logging module
        Returns:
          None
        """
        if self.closeOnError and self.sess:
            self.sess.close()
            self.sess = None  # try to reconnect next time
        else:
            logging.Handler.handleError(self, record)

    def encodePriority(self, facility: Union[str, int], priority: Union[str, int]):
        """
        Encode the facility and priority. You can pass in strings or
        integers - if strings are passed, the facility_names and
        priority_names mapping dictionaries are used to convert them to
        integers.

        Args:
          facility: A string or integer specifying the syslog facility
          priority: A string or integer specifying the syslog priority
        Returns:
          A integer specifying the facility and priority to use.
        """
        try:
            facility = int(facility)
        except ValueError:
            pass
        if isinstance(facility, str):
            if facility in self.facility_names.keys():
                facility = self.facility_names[facility]
            else:
                raise ValueError(f"{facility} is an invalid facility name.")
        elif isinstance(facility, int) and facility > 23:
            raise ValueError(
                f"Valid facilities range from 0 to 23. {facility} does not fall"
                " within that range"
            )
        try:
            priority = int(priority)
        except ValueError:
            pass
        if isinstance(priority, str):
            if priority in self.priority_names.keys():
                priority = self.priority_names[priority]
            else:
                raise ValueError(f"{priority} is an invalid priority name.")
        elif isinstance(priority, int) and priority > 7:
            raise ValueError(
                f"Valid priorities range from 0 to 7. {priority} does not fall"
                " within that range."
            )
        return (facility << 3) | priority

    @classmethod
    def encodeLogLevel(cls, loglevel: str) -> str:
        """

        Args:
          loglevel: A string containing the name of the log level to use or its
              associated integer
        Returns:
          A string containing the properly-formatted log level.
        """
        try:
            loglevel = int(loglevel)
        except ValueError:
            pass
        if isinstance(loglevel, str):
            level = GraylogHandler._map_level_name(loglevel)
        elif isinstance(loglevel, int):
            level = GraylogHandler._map_level_int_to_name(loglevel)
        return level

    def mapPriority(self, levelName: str) -> Union[str, int]:
        """
        Map a logging level name to a key in the priority_names map.
        This is useful in two scenarios: when custom levels are being
        used, and in the case where you can't do a straightforward
        mapping by lowercasing the logging level name because of locale-
        specific issues (see SF #1524081).

        Args:
          levelName: A string specifying the name of the priority level
        Returns:
          An integer specifying the priority level.
        """
        return self.priority_map.get(levelName, 4)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a record.
        Formats the record for GELF and writes it to the server.

        Args:
          record: A LogRecord object
        Returns:
          None
        """
        try:
            msg_payload = GraylogFormatter.format_record(
                record.msg,
                host=self.hostname,
                full_message=record.stack_info,
                level=record.levelname,
                _appname=self.appname,
                _exc_info=record.exc_info,
                _exc_text=record.exc_text,
                _file=record.filename,
                _line=record.lineno,
                _module=record.module,
                _name=record.name,
                _path=record.pathname,
                _process=record.processName,
                _thread=record.threadName,
            )
            msg_payload["_priority"] = self.encodePriority(
                self.facility, self.mapPriority(record.levelname)
            )
            if record.funcName != "<module>":
                msg_payload["_function"] = record.funcName
            self.send(msg_payload)
        except Exception:
            self.handleError(record)
