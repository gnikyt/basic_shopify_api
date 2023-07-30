import pytest
from fastshopifyapi.utils import hmac_verify


def test_hmac_verify_oauth():
    # From Shopify docs: 0Auth
    query_string = {
        "code": "0907a61c0c8d55e99db179b68161bc00",
        "hmac": "700e2dadb827fcc8609e9d5ce208b2e9cdaab9df07390d2cbca10d7c328fc4bf",
        "shop": "some-shop.myshopify.com",
        "state": "0.6784241404160823",
        "timestamp": "1337178173",
    }
    assert hmac_verify("standard", "hush", query_string) is True


def test_hmac_verify_proxy():
    # From Shopify docs: Proxy
    query_string = {
        "extra": ["1", "2"],
        "shop": "shop-name.myshopify.com",
        "path_prefix": "/apps/awesome_reviews",
        "timestamp": "1317327555",
        "signature": "a9718877bea71c2484f91608a7eaea1532bdf71f5c56825065fa4ccabe549ef3",
    }
    assert hmac_verify("proxy", "hush", query_string) is True


def test_hmac_verify_webhook():
    # From Shopify docs: Webhook
    hmac_header_value = "b/rWdZdcB2yqHc0eitdWqmRDdepHw4phdZNa68NHBSY="
    assert hmac_verify("webhook", "hush", '{"xyz":"123"}', hmac_header_value) is True
