from typing import Union
import hashlib
import hmac
import base64


e = "utf-8"


def create_hmac(
    data: Union[dict, str],
    raw: bool = False,
    build_query: bool = False,
    build_query_with_join: bool = False,
    encode: bool = False,
    secret: str = None
) -> str:
    if build_query:
        sorted_keys = sorted(data.keys())
        query_string = []
        for key in sorted_keys:
            value = data[key]
            query_value = ",".join(value) if isinstance(value, (tuple, list)) else value
            query_string.append(f"{key}={query_value}")
        join_key = "&" if build_query_with_join else ""
        data = join_key.join(query_string).encode(e)

    hmac_local = hmac.new(secret.encode(e), data, hashlib.sha256)
    if encode:
        # For webhooks
        return base64.b64encode(hmac_local.digest())
    # For 0Auth and proxy
    return hmac_local.hexdigest().encode(e)


def hmac_verify(source: str, secret: str, params: dict, hmac_header: str = None) -> bool:
    if source == "standard":
        hmac_param = params["hmac"].encode(e)
        params.pop("hmac", None)
        kwargs = {
            "data": params,
            "build_query": True,
            "build_query_with_join": True,
        }
    elif source == "proxy":
        hmac_param = params["signature"].encode(e)
        params.pop("signature", None)
        kwargs = {
            "data": params,
            "build_query": True,
            "build_query_with_join": False,
        }
    elif source == "webhook":
        hmac_param = hmac_header.encode(e)
        kwargs = {
            "data": params.encode(e),
            "raw": True,
            "encode": True,
        }

    hmac_local = create_hmac(**kwargs, secret=secret)
    return hmac.compare_digest(hmac_local, hmac_param)
