#!/usr/bin/env python3


def validate_gelf_payload(payload: dict) -> bool:
    """"""
    required_keys = ["version", "host", "short_message"]
    builtin_keys = required_keys + ["full_message", "timestamp", "level"]
    for rkey in required_keys:
        if rkey not in payload.keys():
            raise KeyError(f"{rkey} is a required key!")
    for key in payload.keys():
        if key not in builtin_keys and not key.startswith("_"):
            raise KeyError(
                f"{rkey} is an invalid key. If using a custom field, it must begin"
                " with an underscore (_)."
            )
    if "_id" in payload.keys():
        raise KeyError("_id is reserved for internal use.")
    return True
