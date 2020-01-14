#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging  # noqa: F401
import pytest  # noqa: F401
import time

from tests.config import (
    HOSTNAME,
    # LOG_LEVEL,
    PORT,
    SERVER,
    # VERIFY,
)  # noqa: F401
from graylogging.graylogging import GraylogFormatter, GraylogHandler

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOG_FORMATTER = GraylogFormatter()
GF = GraylogFormatter()
GH = GraylogHandler(SERVER, port=PORT, appname="pytest")
GH.setFormatter(GF)
# GH.setLevel(logging.DEBUG)
LOGGER.handlers = [GH]
TS = time.time()


# Test to verify py.test
def test_pytest():
    assert 1 == 1


# Test GraylogFormatter class
def test_formatter():
    resp = GF.format(
        "successfully formatted!",
        host=HOSTNAME,
        full_message=(
            "the formatting of this message was successful and also this and"
            " also that and also the other",
        ),
        version="1.1",
        timestamp=time.time(),
        level="1",
        _appname="pytest",
        _foo="bar",
        _success=True
    )
    assert resp["_success"]


# Tests for instantiation of the GraylogHandler class
def test_hostname():
    assert GH.host == SERVER


def test_port():
    assert GH.port == PORT


def test_appname():
    assert GH.appname == "pytest"


def test_client_object():
    obj = GH._connect_graylog()
    assert obj.proto == "https"
    assert obj.host == SERVER
    assert obj.port == PORT
    assert obj.url == f"https://{SERVER}:{PORT}/gelf"
    assert obj.sess


# Tests for various log level methods

def test_debug():
    # I'm still trying to figure out how to verify logging output; assigning to
    # a variable doesn't seem to do anything.
    resp = LOGGER.debug(
        "Successful test from %s via the graylogging logging wrapper!", HOSTNAME
    )
    assert resp is None


def test_info():
    resp = LOGGER.info("JUST FYI")
    assert resp is None


def test_error():
    resp = LOGGER.error("Why did you do that?")
    assert resp is None


def test_critical():
    resp = LOGGER.critical("Mega device errors!")
    assert resp is None


def test_exception():
    resp = LOGGER.exception("You tried to divide by zero, didn't you?")
    assert resp is None


# Tests for miscellany
def test_timestamp_with_timestamp_provided():
    ts = GH._get_timestamp(TS)
    assert ts == TS


def test_timestamp_without_timestamp_provided():
    ts = GH._get_timestamp(None)
    assert ts >= TS


def test_extra_args_with_id():
    extra_args = {"_id": 69, "foo": "bar"}
    with pytest.raises(KeyError):
        GH._extra_args(**extra_args)


def test_extra_args_no_underscore():
    extra_args = {"foo": "bar"}
    with pytest.raises(KeyError):
        GH._extra_args(**extra_args)


def test_extra_args_all_valid():
    extra_args = {"_foo": "bar"}
    resp = GH._extra_args(**extra_args)
    assert resp["_foo"] == "bar"


def test_level_name_valid_int():
    loglevel = 7
    resp = GH.encodeLogLevel(loglevel)
    assert resp == "DEBUG"


def test_level_name_valid_string():
    loglevel = "debug"
    resp = GH.encodeLogLevel(loglevel)
    assert resp == "DEBUG"


def test_level_name_int_str():
    loglevel = "7"
    resp = GH.encodeLogLevel(loglevel)
    assert resp == "DEBUG"


def test_level_name_invalid_int():
    loglevel = 8
    with pytest.raises(ValueError):
        GH.encodeLogLevel(loglevel)


def test_level_name_invalid_string():
    loglevel = "WARMING"
    with pytest.raises(ValueError):
        GH.encodeLogLevel(loglevel)


def test_level_name_invalid_int_str():
    loglevel = "8"
    with pytest.raises(ValueError):
        GH.encodeLogLevel(loglevel)


def test_priority_encoding_both_strings():
    facility = "local6"
    priority = "debug"
    resp = GH.encodePriority(facility, priority)
    assert resp


def test_priority_encoding_str_int():
    facility = "local6"
    priority = 7
    resp = GH.encodePriority(facility, priority)
    assert resp


def test_priority_encoding_int_str():
    facility = 22
    priority = "debug"
    resp = GH.encodePriority(facility, priority)
    assert resp


def test_values_with_stringified_ints():
    facility = "22"
    priority = "7"
    resp = GH.encodePriority(facility, priority)
    assert resp


def test_priority_encoding_invalid_priority_int():
    facility = 22
    priority = 8
    with pytest.raises(ValueError):
        GH.encodePriority(facility, priority)


def test_priority_encoding_invalid_int():
    facility = 24
    priority = 7
    with pytest.raises(ValueError):
        GH.encodePriority(facility, priority)


def test_priority_encoding_invalid_priority_str():
    facility = "local6"
    priority = "d3bug"
    with pytest.raises(ValueError):
        GH.encodePriority(facility, priority)


def test_priority_encoding_invalid_facility_str():
    facility = "locale6"
    priority = "debug"
    with pytest.raises(ValueError):
        GH.encodePriority(facility, priority)


# Tests for the other
