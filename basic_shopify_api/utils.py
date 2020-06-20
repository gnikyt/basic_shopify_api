from .types import DataDict
from typing import Union
import hashlib
import hmac
import base64


def create_hmac(
    data: Union[DataDict, str],
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
        data = join_key.join(query_string).encode("utf-8")

    h = hmac.new(secret, data, hashlib.sha256)
    hmac_local = h.hexdigest().encode("utf-8")
    if encode:
        encoded = base64.urlsafe_b64encode(hmac_local)
        return str(encoded, "utf-8")
    return hmac_local


def hmac_verify(params: DataDict) -> bool:
    if "hmac" not in params:
        return False

    hmac_param = params["hmac"].encode("utf-8")
    params.pop("key", None)
    hmac_local = create_hmac(data=params, build_query=True, build_query_with_join=True)
    return hmac.compare_digest(hmac_local, hmac_param)
