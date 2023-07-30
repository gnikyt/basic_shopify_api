# FastShopifyApi

![Tests](https://github.com/sokoslee/FastShopifyApi/workflows/Package%20Test/badge.svg?branch=master)
[![Coverage](https://coveralls.io/repos/github/osiset/basic_shopify_api/badge.svg?branch=master)](https://coveralls.io/github/osiset/basic_shopify_api?branch=master)
[![PyPi version](https://badge.fury.io/py/basic-shopify-api.svg)](https://pypi.org/project/fastshopifyapi/)

This library extends HTTPX and implements a read-to-use sync/async client for REST and GraphQL API calls to Shopify's API.

Fork from [osiset/basic_shopify_api](https://github.com/gnikyt/basic_shopify_api) with the following changes:
- Rename `basic_shopify_api` to `FastShopifyApi`
- Upgrade Shopify API version
- Fixed some bugs

Support for:

- [X] Sync and async API calls
- [X] REST API
- [X] GraphQL API
- [X] REST rate limiting
- [X] GraphQL cost limiting
- [X] Automatic retries of failed requests
- [X] Support for Retry-After headers
- [X] Pre/post action support

## Table of Contents

- [Installation](#installation)
- [Options Setup](#options)
- [Session Setup](#session)
- [REST Usage](#rest-usage)
- [GraphQL Usage](#graphql-usage)
- [Pre/Post Actions](#prepost-actions)
- [Utilities](#utilities)
- [Development](#development)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Installation

`$ pip install fastshopifyapi`

Requires Python 3.

## Options

`Options()`.

There are a variety of options to take advantage of.

You can simply create a new instance to use all default values if you're using public API mode.

Options available:

- `max_retries` (int), the number of attempts to retry a failed request; default: `2`.
- `retry_on_status` (list), the list of HTTP status codes to watch for, and retry if found; default: `[429, 502, 503, 504]`.
- `headers` (dict), the list of headers to send with each request.
- `time_store` (StateStore), an implementation to store times of requests; default: `TimeMemoryStore`.
- `cost_store` (StateStore), an implementation to store GraphQL response costs; default: `CostMemoryStore`.
- `deferrer` (Deferrer), an implementation to get current time and sleep for time; default: `SleepDeferrer`.
- `rest_limit` (int), the number of allowed REST calls per second; default: `2`.
- `graphql_limit` (int), the cost allowed per second for GraphQL calls; default: `50`.
- `rest_pre_actions` (list), a list of pre-callable actions to fire before a REST request.
- `rest_post_actions` (list), a list of post-callable actions to fire after a REST request.
- `graphql_pre_actions` (list), a list of pre-callable actions to fire before a GraphQL request.
- `graphql_post_actions` (list), a list of post-callable actions to fire after a GraphQL request.
- `version` (str), the API version to use for all requests; default: `2020-04`.
- `mode` (str), the type of API to use either `public` or `private`; default: `public`.

Example:

```python
opts = Options()
opts.version = "unstable"
opts.mode = "private"
```

## Session

Create a session to use with a client. Depending on if you're accessing the API public or privately, then you will need to fill different values.

`Session(domain, key, password, secret)`.

For public access, you will need to fill in:

- `domain`, the full myshopify domain.
- `password`, the shop's access token.
- `secret`, the app's secret key.

For private access, you will need to fill in:

- `domain`, the full myshopify domain.
- `key`, the shop's key.
- `password`, the shop's password.

Example:

```python
from fastshopifyapi import Session

session = Session(domain="john-doe.myshopify.com", key="abc", password="123")
```

## REST Usage

`rest(method, path[, params, headers])`.

- `method` (str), being one of `get`, `post`, `put`, or `delete`.
- `path` (str), being an API path, example: `/admin/api/shop.json`.
- `params` (dict) (optional), being a dict of query or json data.
- `headers` (dict) (optional), being a dict of additional headers to pass with the request.

### REST Sync

Example:

```python
from fastshopifyapi import Client

with Client(sess, opts) as client:
    shop = client.rest("get", "/admin/api/shop.json", {"fields": "name,email"})
    print(shop.response)
    print(shop.body["name"])

    # returns the following:
    # RestResult(
    #   response=The HTTPX response object,
    #   body=A dict of JSON response, or None if errors,
    #   errors=A dict of error response (if possible), or None for no errors, or the exception error,
    #   status=The HTTP status code,
    #   link=A RestLink object of next/previous pagination info,
    #   retries=Number of retires for the request
    # )
```

### REST Async

Example:

```python
from fastshopifyapi import AsyncClient

# ...

async with AsyncClient(sess, opts) as client:
    shop = await client.rest("get", "/admin/api/shop.json", {"fields": "name,email"})
    print(shop.response)
    print(shop.body["name"])

    # returns the following:
    # RestResult(
    #   response=The HTTPX response object,
    #   body=A dict of JSON response, or None if errors,
    #   errors=A dict of error response (if possible), or None for no errors, or the exception error,
    #   status=The HTTP status code,
    #   link=A RestLink object of next/previous pagination info,
    #   retries=Number of retires for the request
    # )
```

## GraphQL Usage

`graphql(query[, variables])`.

- `query` (str), being the GraphQL query string.
- `variables` (dict) (optional), being the variables for your query or mutation.

### GraphQL Sync

Example:

```python
from fastshopifyapi import Client

# ...

with Client(sess, opts) as client:
    shop = client.graphql("{ shop { name } }")
    print(shop.response)
    print(shop.body["data"]["shop"]["name"])

    # returns the following:
    # ApiResult(
    #   response=The HTTPX response object,
    #   body=A dict of JSON response, or None if errors,
    #   errors=A dict of error response (if possible), or None for no errors, or the exception error,
    #   status=The HTTP status code,
    #   retries=Number of retires for the request,
    # )
```

### GraphQL Async

Example:

```python
from fastshopifyapi import AsyncClient

# ...

async with AsyncClient(sess, opts) as client:
    shop = await client.graphql("{ shop { name } }")
    print(shop.response)
    print(shop.body["data"]["name"])

    # returns the following:
    # ApiResult(
    #   response=The HTTPX response object,
    #   body=A dict of JSON response, or None if errors,
    #   errors=A dict of error response (if possible), or None for no errors, or the exception error,
    #   status=The HTTP status code,
    #   link=A RestLink object of next/previous pagination info,
    #   retries=Number of retires for the request
    # )
```

## Pre/Post Actions

To register a pre or post action for REST or GraphQL, simply append it to your options setup.

```python
from fastshopifyapi import Options, Client


def say_hello(inst):
    """inst is the current client instance, either Client or AsyncClient"""
    print("hello")


def say_world(inst, result):
    """
    inst is the current client instance, either Client or AsyncClient.
    result is either RestResult or GraphQLResult object.
    """
    print("world")


opts = Options()
opts.rest_pre_actions = [say_hello]
opts.rest_post_ations = [say_world]

sess = Session(domain="john-doe.myshopify.com", key="abc", password="134")

with Client(sess, opts) as client:
    shop = client.rest("get", "/admin/api/shop.json")
    print(shop)
    # Output: "hello" "world" <ApiResult>
```

## Utilities

This will be expanding, but as of now there are utilities to help verify HMAC for 0Auth/URL, proxy requests, and webhook data.

### 0Auth/URL

```python
from fastshopifyapi.utils import hmac_verify

params = request.args  # some method to get a dict of query params
verified = hmac_verify("standard", "secret key", params)
print(f"Verified? {verified}")
```

### Proxy

```python
from fastshopifyapi.utils import hmac_verify

params = request.args  # some method to get a dict of query params
verified = hmac_verify("proxy", "secret key", params)
print(f"Verified? {verified}")
```

### Webhook

```python
from fastshopifyapi.utils import hmac_verify

hmac_header = request.headers.get("x-shopify-hmac-sha256")  # some method to get the HMAC header
params = request.get_data(as_text=True)  # some method to get a JSON str of request data
verified = hmac_verify("webhook", "secret key", params, hmac_header)
print(f"Verified? {verified}")
```

## Development

`python -m venv env && source env/bin/activate`

`python -m pip install -r requirements.txt`

## Testing

`make test`.

For coverage reports, use `make cover` or `make cover-html`.

## Documentation

See [this Github page](https://osiset.com/basic_shopify_api/) or view `docs/`.

## License

This project is released under the MIT [license](https://github.com/osiset/basic_shopify_api/blob/master/LICENSE).

## Misc

Using PHP? [Check out Basic-Shopify-API](https://github.com/osiset/Basic-Shopify-API).
