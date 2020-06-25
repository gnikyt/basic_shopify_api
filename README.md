# basic_shopify_api

![Tests](https://github.com/osiset/basic_shopify_api/workflows/Package%20Test/badge.svg?branch=master)
[![Coverage](https://coveralls.io/repos/github/osiset/basic_shopify_api/badge.svg?branch=master)](https://coveralls.io/github/osiset/basic_shopify_api?branch=master)
[![PyPi version](https://pypip.org/project/basic_shopify_api)](https://badge.fury.io/py/basic_shopify_api.svg)

This library extends HTTPX and implements a read-to-use sync/async client for REST and GraphQL API calls to Shopify's API.

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
  - [Testing](#testing)
  - [License](#license)

## Installation

*Note: currently not published.*

`pip install basic_shopify_api`

## Options

`Options()`.

There's a huge verity of options/configuration to takr advantage of, but all are optional.

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

    from basic_shopify_api import Session
    
    session = Session(domain="john-doe.myshopify.com", key="abc", password="123")

## REST Usage

`rest(method, path[, params, headers])`.

- `method` (str), being one of `get`, `post`, `put`, or `delete`.
- `path` (str), being an API path, example: `/admin/api/shop.json`.
- `params` (dict) (optional), being a dict of query or json data.
- `headers` (dict) (optional), being a dict of additional headers to pass with the request.

### Sync

Example:

    from basic_shopify_api import Client
    
    # ...
    
    with Client(sess, opts) as client:
      shop = client.rest("get", "/admin/api/shop.json", {"fields": "name,email"}})
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

### Async

Example:

    from basic_shopify_api import AsyncClient
    
    # ...
    
    async with AsyncClient(sess, opts) as client:
      shop = await client.rest("get", "/admin/api/shop.json", {"fields": "name,email"}})
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

## GraphQL Usage

`graphql(query[, variables])`.

- `query` (str), being the GraphQL query string.
- `variables` (dict) (optional), being the variables for your query or mutation.

### Sync

Example:

    from basic_shopify_api import Client
    
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

### Async

Example:

    from basic_shopify_api import AsyncClient
    
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

## Pre/Post Actions

To register a pre or post action for REST or GraphQL, simply append it to your options setup.

    from basic_shopify_api import Options, Client
    
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
    
## Utilities

This will be expanding, but as of now there are utilities to help verify HMAC for 0Auth/URL, proxy requests, and webhook data.

### 0Auth/URL

    from basic_shopify_api.utils import hmac_verify
    
    params = request.args # some method to get a dict of query params
    verified = hmac_verify("standard", "secret key", params)
    print("Verified? {verified}")

### Proxy

    from basic_shopify_api.utils import hmac_verify
    
    params = request.args # some method to get a dict of query params
    verified = hmac_verify("proxy", "secret key", params)
    print("Verified? {verified}")

### Webhook

    from basic_shopify_api.utils import hmac_verify
    
    hmac_header = request.headers.get("x-shopify-hmac-sha256") # some method to get the HMAC header
    params = request.json # some method to get a dict of JSON data
    verified = hmac_verify("webhook", "secret key", params, hmac_header)
    print("Verified? {verified}")

## Testing

`make test`, for coverage reports, use `make cover` or `make cover-html`.

## License

This project is released under the MIT [license](https://github.com/osiset/basic_shopify_api/blob/master/LICENSE).
