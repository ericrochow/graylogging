#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import time

import pytest

from tests.config import HOSTNAME, LOG_LEVEL, PORT, SERVER, VERIFY
from graylogging.client import Graylog

GL = Graylog(SERVER, port=PORT, verify=VERIFY, log_level=LOG_LEVEL)

PAYLOAD_SEED = {
    "_application": "graylogging_client",
    "_testing": True,
    "_exc_info": None,
    "_exc_text": None,
    "_file": "test_http_client.py",
    "_line": 69,
    "_module": "test_http_client",
    "_name": "root",
    "_path": "test_http_client",
    "_priority": "666",
    "_process": "MainProcess",
    "_thread": "MainThread",
    "host": HOSTNAME,
    "level": "DEBUG",
    "short_message": (
        f"Successful test from {HOSTNAME} via the graylogging gelf client!"
    ),
    "timestamp": time.time(),
    "version": "1.1",
}


# Test to verify py.test
def test_pytest():
    assert 1 == 1


# Tests for the `validate_gelf_payload` method of the Graylog class
def test_missing_version():
    VERSION = PAYLOAD_SEED.pop("version")
    with pytest.raises(KeyError):
        GL._validate_gelf_payload(PAYLOAD_SEED)  # noqa: F841
    PAYLOAD_SEED["version"] = VERSION


def test_missing_host():
    HOST = PAYLOAD_SEED.pop("host")
    with pytest.raises(KeyError):
        GL._validate_gelf_payload(PAYLOAD_SEED)  # noqa: F841
    PAYLOAD_SEED["host"] = HOST


def test_missing_short_message():
    SHORT_MESSAGE = PAYLOAD_SEED.pop("short_message")
    with pytest.raises(KeyError):
        GL._validate_gelf_payload(PAYLOAD_SEED)  # noqa: F841
    PAYLOAD_SEED["short_message"] = SHORT_MESSAGE


def test_id_key():
    PAYLOAD_SEED["_id"] = "69420666"
    with pytest.raises(KeyError):
        GL._validate_gelf_payload(PAYLOAD_SEED)  # noqa: F841
    PAYLOAD_SEED.pop("_id")


def test_valid_gelf():
    valid = GL._validate_gelf_payload(PAYLOAD_SEED)
    assert valid


def test_with_custom_field():
    PAYLOAD_SEED["_foo"] = "bar"
    valid = GL._validate_gelf_payload(PAYLOAD_SEED)
    assert valid
    PAYLOAD_SEED.pop("_foo")


def test_with_string_level():
    LEVEL = PAYLOAD_SEED.pop("level")
    PAYLOAD_SEED["level"] = "warning"
    valid = GL._validate_gelf_payload(PAYLOAD_SEED)
    assert valid
    PAYLOAD_SEED["level"] = LEVEL


def test_with_int_level():
    LEVEL = PAYLOAD_SEED.pop("level")
    PAYLOAD_SEED["level"] = 7
    valid = GL._validate_gelf_payload(PAYLOAD_SEED)
    assert valid
    PAYLOAD_SEED["level"] = LEVEL


def test_with_str_int_level():
    LEVEL = PAYLOAD_SEED.pop("level")
    PAYLOAD_SEED["level"] = "7"
    valid = GL._validate_gelf_payload(PAYLOAD_SEED)
    assert valid
    PAYLOAD_SEED["level"] = LEVEL


# Tests for the `send_gelf` method of the Graylog class
def test_gelf_post():
    resp = GL.send_gelf(PAYLOAD_SEED)  # noqa: F841
    assert resp["status_code"] == 202
    # assert 1 == 2
