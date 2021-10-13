#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
from typing import Optional

from graylogging.tools import validate_gelf_payload


class HTTPGELF:
    """"""

    def __init__(
        self,
        host: str,
        port: Optional[int] = 12201,
        protocol: str = "https",
        timeout: int = 30,
        verify: bool = True,
    ) -> None:
        self.proto = protocol
        self.host = host
        self.port = port
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.timeout = timeout
        self.verify = verify
        self.sess = requests.Session()
        self.url = f"{self.proto}://{self.host}:{self.port}/gelf"

    def _post(self, body: dict) -> dict:
        """
        Sends an HTTP POST request.

        Args:
          body: A dictionary containing the JSON-formatted GELF payload
        Returns:
          The result of the POST request.
        """
        resp = self.sess.post(
            self.url,
            json=body,
            headers=self.headers,
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
            if "error_class" in resp.keys():
                resp.raise_for_status()
            else:
                return resp
        else:
            resp.raise_for_status()

    def _validate_gelf_payload(self, body: dict) -> bool:
        """
        Validate the GELF payload to make sure proper keys are included and no
            reserved keys are used.

        Args:
          body: A dictionary containing the GELF payload to post to the server
        Returns:
          A boolean specifying whether the GELF payload is valid.
        Raises:
          KeyError: {key} is an invalid key. If using a custom field, it must
              begin with an underscore (_).
          KeyError: _id is reserved for internal use.
        """
        required_keys = ["version", "host", "short_message"]
        builtin_keys = required_keys + ["full_message", "timestamp", "level"]
        for rkey in required_keys:
            if rkey not in body.keys():
                raise KeyError(f"{rkey} is a required key!")
        for key in body.keys():
            if key not in builtin_keys and not key.startswith("_"):
                raise KeyError(
                    f"{key} is an invalid key. If using a custom field, it "
                    "must begin with an underscore (_)."
                )
        if "_id" in body.keys():
            raise KeyError("_id is reserved for internal use.")
        return True

    def send_gelf(self, body: dict) -> dict:
        """
        Sends a message to Graylog using GELF.

        Args:
          body: A dict containing the JSON-formatted GELF payload
        Returns:
          The results of the POST.
        """
        if validate_gelf_payload(body):
            return self._post(body)
