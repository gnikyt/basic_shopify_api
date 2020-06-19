from setuptools import setup

NAME="basic_shopify_api"
exec(open("basic_shopify_api/__version__.py").read())
DESCRIPTION="A REST/GraphQL client for Shopify API using HTTPX"
LONG_DESCRIPTION="""\
This library extends HTTPX and implements a read-to-use client for
REST and GraphQL API calls to Shopify API"""

setup(name=NAME,
  version=VERSION,
  description=DESCRIPTION,
  long_description=LONG_DESCRIPTION,
  author="osiset",
  author_email="tyler@osiset.com",
  url="https://github.com/osiset/basic_shopify_api",
  packages=["basic_shopify_api"],
  license="MIT License",
  install_requires=[
    "httpx>=0.13"
  ],
  test_suite="test",
  tests_require=[
    "mock>=1.0.1",
  ],
  platforms="Any"
)
