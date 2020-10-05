#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests

from graylogging.tools import validate_gelf_payload


class HTTPGELF(object):
    """"""

    def __init__(
        self,
        host,
        port=12201,
        protocol="https",
        timeout=30,
        verify=True,
        raise_on_error=True,
        log_level="WARNING",
    ):
        self.proto = protocol
        self.host = host
        self.port = port
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # self.auth = ()
        self.timeout = timeout
        self.verify = verify
        self.raise_on_error = raise_on_error
        self.sess = requests.Session()
        self.url = f"{self.proto}://{self.host}:{self.port}/gelf"

    def _post(self, params, raw_json=True):
        """
        Sends an HTTP POST request.

        Args:
          params: A dictionary containing the JSON-formatted GELF payload
          raw_json: A boolean specifying whether to return raw JSON (optional,
              defaults to True)
        Returns:
          The result of the POST request.
        """
        resp = self.sess.post(
            self.url,
            json=params,
            headers=self.headers,
            # auth=self.creds,
            timeout=self.timeout,
            verify=self.verify,
        )
        if resp.ok:
            status_code = resp.status_code
            if resp.content:
                resp = resp.json()
                resp["status_code"] = status_code
            else:
                resp = {}
            resp["status_code"] = status_code
            if self.raise_on_error and "error_class" in resp.keys():
                resp.raise_for_status()
            elif raw_json:
                return resp
            else:
                return resp.text
        else:
            resp.raise_for_status()

    def _validate_gelf_payload(self, payload):
        """"""
        required_keys = ["version", "host", "short_message"]
        builtin_keys = required_keys + ["full_message", "timestamp", "level"]
        for rkey in required_keys:
            if rkey not in payload.keys():
                raise KeyError(f"{rkey} is a required key!")
        for key in payload.keys():
            if key not in builtin_keys and not key.startswith("_"):
                raise KeyError(
                    f"{key} is an invalid key. If using a custom field, it "
                    "must begin with an underscore (_)."
                )
        if "_id" in payload.keys():
            raise KeyError("_id is reserved for internal use.")
        return True

    def send_gelf(self, payload):
        """
        Sends a message to Graylog using GELF.

        Args:
          payload: A dict containing the JSON-formatted GELF payload
        Returns:
          The results of the POST.
        """
        if validate_gelf_payload(payload):
            return self._post(payload)
